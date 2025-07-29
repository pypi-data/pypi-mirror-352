from typing import BinaryIO

import ffmpeg

from ._base import BaseStep


class Mp4ToWebpStep(BaseStep):
    def __init__(
        self,
        input_file: BinaryIO,
        output_file: BinaryIO,
        *,
        width: int,
        frame_rate: int,
    ) -> None:
        self._input_file = input_file
        self._output_file = output_file
        self._width = width
        self._frame_rate = frame_rate

    async def run(self) -> None:
        (
            ffmpeg
            .input(self._input_file.name)
            .filter('scale', self._width, -1)
            .output(
                self._output_file.name,
                vcodec='libwebp',  # use the WebP encoder
                loop=0,  # 0 = infinite loop
                lossless=0,  # 1 = lossless; 0 = lossy
                compression_level=6,  # 0–6 (higher = slower but better)
                **{'qscale:v': 50},  # quality: 0 (best)–100 (worst)
                r=self._frame_rate,  # output framerate
            )
            .overwrite_output()
            .run()
        )
