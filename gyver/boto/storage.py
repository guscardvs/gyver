import logging
from typing import BinaryIO
from typing import Optional
from typing import Protocol

from botocore.exceptions import ClientError

from gyver import utils
from gyver.config import ProviderConfig
from gyver.config import from_config
from gyver.exc import GyverError

from ._client import make_client


class StorageConfig(ProviderConfig):
    _prefix_ = "storage"

    access_key_id: str
    secret_access_key: str
    bucket_name: str
    region_name: str
    presigned_expiration: int = 3600
    endpoint_url: Optional[str] = None


class FileNotFound(GyverError, FileNotFoundError):
    pass


class ReadableBuffer(Protocol):
    def read(self) -> bytes:
        ...


class StorageProvider:
    def __init__(self, config: Optional[StorageConfig] = None) -> None:
        self._config = config or from_config(StorageConfig)

    @utils.lazyfield
    def client(self):
        kwargs = {
            "region_name": self._config.region_name,
            "aws_access_key_id": self._config.access_key_id,
            "aws_secret_access_key": self._config.secret_access_key,
        }
        if endpoint_url := self._config.endpoint_url:
            kwargs["endpoint_url"] = endpoint_url
        return make_client("s3", **kwargs)

    @property
    def config(self):
        return self._config

    def _generate_presigned_url(
        self,
        method: str,
        object_name: str,
        bucket_name: Optional[str] = None,
    ):
        bucket_name = bucket_name or self._config.bucket_name
        try:
            response = self.client.generate_presigned_url(
                method,
                Params={"Bucket": bucket_name, "Key": object_name},
                ExpiresIn=self._config.presigned_expiration,
            )
        except ClientError as e:
            logging.error(e)
            return object_name
        else:
            return response

    def upload_file(
        self,
        buf: BinaryIO,
        object_name: str,
        bucket_name: Optional[str] = None,
    ):
        bucket_name = bucket_name or self._config.bucket_name
        self.client.upload_fileobj(buf, bucket_name, object_name)

    def generate_presigned_get(
        self, object_name: str, bucket_name: Optional[str] = None
    ):
        bucket_name = bucket_name or self._config.bucket_name
        return (
            self._generate_presigned_url(
                "get_object", object_name, bucket_name
            )
            if self.is_key(object_name, bucket_name)
            else object_name
        )

    def is_key(
        self, object_name: str, bucket_name: Optional[str] = None
    ) -> bool:
        bucket_name = bucket_name or self._config.bucket_name
        try:
            self.client.head_object(Bucket=bucket_name, Key=object_name)
        except ClientError:
            return False
        else:
            return True

    def get_file(
        self, object_name: str, bucket_name: Optional[str] = None
    ) -> ReadableBuffer:
        bucket_name = bucket_name or self._config.bucket_name
        if not self.is_key(object_name, bucket_name):
            raise FileNotFound(
                f"Object {object_name} not found in {bucket_name} bucket"
            )
        response = self.client.get_object(Bucket=bucket_name, Key=object_name)
        return response["Body"]
