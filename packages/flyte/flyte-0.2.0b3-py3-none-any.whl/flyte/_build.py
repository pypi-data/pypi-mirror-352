from __future__ import annotations

from ._api_commons import syncer
from ._image import Image


@syncer.wrap
async def build(image: Image) -> str:
    """
    Build an image. The existing async context will be used.

    Example:
    ```
    import flyte
    image = flyte.Image("example_image")
    if __name__ == "__main__":
        asyncio.run(flyte.build.aio(image))
    ```

    :param image: The image(s) to build.
    :return: The image URI.
    """
    from flyte._internal.imagebuild.image_builder import ImageBuildEngine

    return await ImageBuildEngine.build(image)
