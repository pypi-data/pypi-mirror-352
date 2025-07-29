from __future__ import annotations

import asyncio
import json
import typing
from typing import ClassVar, Dict, Optional, Tuple

from async_lru import alru_cache
from pydantic import BaseModel
from typing_extensions import Protocol

from flyte._image import Architecture, Image
from flyte._logging import logger


class ImageBuilder(Protocol):
    async def build_image(self, image: Image, dry_run: bool) -> str: ...


class ImageChecker(Protocol):
    @classmethod
    async def image_exists(
        cls, repository: str, tag: str, arch: Tuple[Architecture, ...] = ("linux/amd64",)
    ) -> bool: ...


class DockerAPIImageChecker(ImageChecker):
    """
    Unfortunately only works for docker hub as there's no way to get a public token for ghcr.io. See SO:
    https://stackoverflow.com/questions/57316115/get-manifest-of-a-public-docker-image-hosted-on-docker-hub-using-the-docker-regi
    The token used here seems to be short-lived (<1 second), so copy pasting doesn't even work.
    """

    @classmethod
    async def image_exists(cls, repository: str, tag: str, arch: Tuple[Architecture, ...] = ("linux/amd64",)) -> bool:
        import httpx

        if "/" in repository:
            if not repository.startswith("library/"):
                raise ValueError("This checker only works with Docker Hub")
        else:
            repository = f"library/{repository}"

        auth_url = "https://auth.docker.io/token"
        service = "registry.docker.io"
        scope = f"repository:{repository}:pull"

        async with httpx.AsyncClient() as client:
            # Get auth token
            auth_response = await client.get(auth_url, params={"service": service, "scope": scope})
            if auth_response.status_code != 200:
                raise Exception(f"Failed to get auth token: {auth_response.status_code}")
            token = auth_response.json()["token"]

            manifest_url = f"https://registry-1.docker.io/v2/{repository}/manifests/{tag}"
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": (
                    "application/vnd.docker.distribution.manifest.v2+json,"
                    "application/vnd.docker.distribution.manifest.list.v2+json"
                ),
            }
            manifest_response = await client.get(manifest_url, headers=headers)

            if manifest_response.status_code != 200:
                raise Exception(f"Failed to get manifest: {manifest_response.status_code}")
            manifest_list = manifest_response.json()["manifests"]
            architectures = [f"{x['platform']['os']}/{x['platform']['architecture']}" for x in manifest_list]

            if set(architectures) >= set(arch):
                logger.debug(f"Image {repository}:{tag} found for architecture(s) {arch}, has {architectures}")
                return True
            else:
                logger.debug(f"Image {repository}:{tag} not found for architecture(s) {arch}, only has {architectures}")
                return False


class LocalDockerCommandImageChecker(ImageChecker):
    command_name: ClassVar[str] = "docker"

    @classmethod
    async def image_exists(cls, repository: str, tag: str, arch: Tuple[Architecture, ...] = ("linux/amd64",)) -> bool:
        # Check if the image exists locally by running the docker inspect command
        process = await asyncio.create_subprocess_exec(
            cls.command_name,
            "manifest",
            "inspect",
            f"{repository}:{tag}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if stderr and "manifest unknown" in stderr.decode():
            logger.debug(f"Image {repository}:{tag} not found using the docker command.")
            return False

        if process.returncode != 0:
            raise RuntimeError(f"Failed to run docker image inspect {repository}:{tag}")

        inspect_data = json.loads(stdout.decode())
        if "manifests" not in inspect_data:
            raise RuntimeError(f"Invalid data returned from docker image inspect for {repository}:{tag}")
        manifest_list = inspect_data["manifests"]
        architectures = [f"{x['platform']['os']}/{x['platform']['architecture']}" for x in manifest_list]
        if set(architectures) >= set(arch):
            logger.debug(f"Image {repository}:{tag} found for architecture(s) {arch}, has {architectures}")
            return True

        # Otherwise write a message and return false to trigger build
        logger.debug(f"Image {repository}:{tag} not found for architecture(s) {arch}, only has {architectures}")
        return False


class LocalPodmanCommandImageChecker(LocalDockerCommandImageChecker):
    command_name: ClassVar[str] = "podman"


class ImageBuildEngine:
    """
    ImageBuildEngine contains a list of builders that can be used to build an ImageSpec.
    """

    _REGISTRY: typing.ClassVar[typing.Dict[str, Tuple[ImageBuilder, int]]] = {}
    _SEEN_IMAGES: typing.ClassVar[typing.Dict[str, str]] = {
        # Set default for the auto container. See Image._identifier_override for more info.
        "auto": Image.auto().uri,
    }

    @classmethod
    def register(cls, builder_type: str, image_builder: ImageBuilder, priority: int = 5):
        cls._REGISTRY[builder_type] = (image_builder, priority)

    @classmethod
    def get_registry(cls) -> Dict[str, Tuple[ImageBuilder, int]]:
        return cls._REGISTRY

    @staticmethod
    @alru_cache
    async def image_exists(image: Image) -> bool:
        if image.base_image is not None and not image._layers:
            logger.debug(f"Image {image} has a base image: {image.base_image} and no layers. Skip existence check.")
            return True
        assert image.registry is not None, f"Image registry is not set for {image}"
        assert image.name is not None, f"Image name is not set for {image}"

        repository = image.registry + "/" + image.name
        tag = image._final_tag

        if tag == "latest":
            logger.debug(f"Image {image} has tag 'latest', skip existence check, always build")
            return True

        # Can get a public token for docker.io but ghcr requires a pat, so harder to get the manifest anonymously.
        checkers = [LocalDockerCommandImageChecker, LocalPodmanCommandImageChecker, DockerAPIImageChecker]
        for checker in checkers:
            try:
                exists = await checker.image_exists(repository, tag, tuple(image.platform))
                logger.debug(f"Image {image} {exists=} in registry")
                return exists
            except Exception as e:
                logger.debug(f"Error checking image existence with {checker.__name__}: {e}")
                continue

        # If all checkers fail, then assume the image exists. This is current flytekit behavior
        logger.info(f"All checkers failed to check existence of {image.uri}, assuming it does exists")
        return True

    @classmethod
    @alru_cache
    async def build(
        cls, image: Image, builder: Optional[str] = None, dry_run: bool = False, force: bool = False
    ) -> str:
        """
        Build the image. Images to be tagged with latest will always be built. Otherwise, this engine will check the
        registry to see if the manifest exists.

        :param image:
        :param builder:
        :param dry_run: Tell the builder to not actually build. Different builders will have different behaviors.
        :param force: Skip the existence check. Normally if the image already exists we won't build it.
        :return:
        """
        # Always trigger a build if this is a dry run since builder shouldn't really do anything, or a force.
        if force or dry_run or not await cls.image_exists(image):
            logger.info(f"Image {image.uri} does not exist in registry or force/dry-run, building...")

            # Validate the image before building
            image.validate()

            # If builder is not specified, use the first registered builder
            img_builder = ImageBuildEngine._get_builder(builder)

            result = await img_builder.build_image(image, dry_run=dry_run)
            return result
        else:
            logger.info(f"Image {image.uri} already exists in registry. Skipping build.")
            return image.uri

    @classmethod
    def _get_builder(cls, builder: Optional[str]) -> ImageBuilder:
        if not builder:
            from .docker_builder import DockerImageBuilder

            return DockerImageBuilder()
        if builder not in cls._REGISTRY:
            raise AssertionError(f"Image builder {builder} is not registered.")
        return cls._REGISTRY[builder][0]


class ImageCache(BaseModel):
    image_lookup: Dict[str, str]
    serialized_form: str | None = None

    @property
    def to_transport(self) -> str:
        """
        :return: returns the serialization context as a base64encoded, gzip compressed, json string
        """
        # This is so that downstream tasks continue to have the same image lookup abilities
        import base64
        import gzip
        from io import BytesIO

        if self.serialized_form:
            return self.serialized_form
        json_str = self.model_dump_json(exclude={"serialized_form"})
        buf = BytesIO()
        with gzip.GzipFile(mode="wb", fileobj=buf, mtime=0) as f:
            f.write(json_str.encode("utf-8"))
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    @classmethod
    def from_transport(cls, s: str) -> ImageCache:
        import base64
        import gzip

        compressed_val = base64.b64decode(s.encode("utf-8"))
        json_str = gzip.decompress(compressed_val).decode("utf-8")
        val = cls.model_validate_json(json_str)
        val.serialized_form = s
        return val
