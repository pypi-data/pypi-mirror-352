from typing import BinaryIO

from moviepy import VideoFileClip

from ._base import BaseStep


class Mp4SizeStep(BaseStep):
    def __init__(
        self,
        file: BinaryIO,
    ) -> None:
        self._file = file

    async def run(self) -> tuple[int, int]:
        return VideoFileClip(self._file.name).size
