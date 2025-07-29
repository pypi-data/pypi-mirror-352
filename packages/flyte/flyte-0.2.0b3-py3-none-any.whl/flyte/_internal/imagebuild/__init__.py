import asyncio
from typing import List

from flyte._image import Image
from flyte._internal.imagebuild.docker_builder import DockerImageBuilder


async def build(images: List[Image]) -> List[str]:
    builder = DockerImageBuilder()
    ts = [asyncio.create_task(builder.build_image(image)) for image in images]
    return list(await asyncio.gather(*ts))
