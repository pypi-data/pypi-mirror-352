from typing import BinaryIO, Literal

from aiobotocore.session import AioSession, get_session

from ._base import BaseStep


class AwsSession:
    _session: AioSession | None = None

    @classmethod
    def get(cls) -> AioSession:
        if cls._session is None:
            cls._session = get_session()

        return cls._session


class UploadToS3Step(BaseStep):
    def __init__(
        self,
        file: BinaryIO,
        *,
        aws_region: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        aws_s3_bucket: str,
        aws_s3_object_key: str,
        content_type: Literal['image/webp'],
    ) -> None:
        self._file = file
        self._aws_region = aws_region
        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key
        self._aws_s3_bucket = aws_s3_bucket
        self._aws_s3_object_key = aws_s3_object_key
        self._content_type = content_type

    async def run(self) -> None:
        aws_session = AwsSession.get()

        async with aws_session.create_client(
            's3',
            region_name=self._aws_region,
            aws_access_key_id=self._aws_access_key_id,
            aws_secret_access_key=self._aws_secret_access_key,
        ) as s3_client:
            await s3_client.put_object(
                Bucket=self._aws_s3_bucket,
                Key=self._aws_s3_object_key,
                Body=self._file,
                ContentType=self._content_type,
            )
