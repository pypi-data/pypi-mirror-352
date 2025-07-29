from typing import BinaryIO

import ffmpeg

from ._base import BaseStep


class MinimizeMp4Step(BaseStep):
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
        (
            ffmpeg
            .input(self._input_file.name)
            # scale width to `self._width`, auto‐compute an even‐numbered height
            .filter('scale', self._width, -2)
            .output(
                self._output_file.name,
                vcodec='libx264',
                crf=self._quality,
                preset='veryslow',            # you can choose 'fast', 'slow', etc.
                acodec='aac',               # re‐encode audio to AAC
                audio_bitrate='96k',        # optional: shrink audio bitrate
                movflags='+faststart',       # move metadata to front for streaming
                pix_fmt='yuv420p',
            )
            .run(overwrite_output=True)
        )
