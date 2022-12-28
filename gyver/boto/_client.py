from typing import TYPE_CHECKING
from typing import Any
from typing import Literal
from typing import overload

from boto3 import Session

if TYPE_CHECKING:
    from mypy_boto3_s3.client import S3Client
    from mypy_boto3_sqs.client import SQSClient


@overload
def make_client(service_name: Literal["s3"], **params) -> "S3Client":
    ...


@overload
def make_client(service_name: Literal["sqs"], **params) -> "SQSClient":
    ...


def make_client(service_name: Literal["s3", "sqs"], **params: Any) -> Any:
    return Session().client(service_name, **params)
