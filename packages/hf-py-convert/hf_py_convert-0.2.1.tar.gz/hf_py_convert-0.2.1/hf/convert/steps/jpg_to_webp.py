from typing import BinaryIO

from PIL import Image

from ._base import BaseStep


class JpgToWebpStep(BaseStep):
    def __init__(
        self,
        input_file: BinaryIO,
        output_file: BinaryIO,
        *,
        width: int,
        quality: int,
    ) -> None:
        self._input_file = input_file
        self._output_file = output_file
        self._width = width
        self._quality = quality

    async def run(self) -> None:
        with Image.open(self._input_file.name) as image:
            image = image.convert('RGB')
            width, height = image.size
            new_width = self._width
            new_height = int(height * (new_width / width))
            resized = image.resize((new_width, new_height), Image.LANCZOS)
            resized.save(
                self._output_file,
                format='WEBP',
                lossless=False,
                quality=self._quality,
            )
