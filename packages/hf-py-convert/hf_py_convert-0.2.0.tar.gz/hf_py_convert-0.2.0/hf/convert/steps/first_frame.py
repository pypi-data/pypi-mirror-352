from typing import BinaryIO

from PIL import Image

from ._base import BaseStep


class FirstFrameStep(BaseStep):
    def __init__(
        self,
        input_file: BinaryIO,
        output_file: BinaryIO,
        *,
        quality: int,
    ) -> None:
        self._input_file = input_file
        self._output_file = output_file
        self._quality = quality

    async def run(self) -> None:
        with Image.open(self._input_file.name) as image:
            image.seek(0)
            first_frame = image.convert('RGB')
            first_frame.save(
                self._output_file,
                format='WEBP',
                lossless=False,
                quality=self._quality,
                method=6,
            )
