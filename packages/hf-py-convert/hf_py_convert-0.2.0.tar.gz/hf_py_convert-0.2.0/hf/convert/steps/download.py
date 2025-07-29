from typing import BinaryIO

import httpx

from ._base import BaseStep


class DownloadStep(BaseStep):
    def __init__(
        self,
        file: BinaryIO,
        *,
        url: str,
    ) -> None:
        self._file = file
        self._url = url

    async def run(self) -> None:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(self._url)
            self._file.write(response.content)
