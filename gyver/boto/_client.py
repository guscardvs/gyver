from typing import TYPE_CHECKING
from typing import Any
from typing import Literal

from boto3 import Session

if TYPE_CHECKING:
    from mypy_boto3_s3.client import S3Client


def make_client(service_name: Literal["s3"], **params: Any) -> "S3Client":
    return Session().client(service_name, **params)
