from typing import TYPE_CHECKING
from typing import Literal
from typing import Optional
from typing import Union
from typing import overload

from boto3 import Session

from gyver.config import ProviderConfig
from gyver.config import from_config
from gyver.utils import make_singleton

if TYPE_CHECKING:
    from mypy_boto3_s3.client import S3Client
    from mypy_boto3_sqs.client import SQSClient


class AWSCredentialsConfig(ProviderConfig):
    __prefix__ = "aws"

    access_key_id: str
    secret_access_key: str
    region_name: str
    endpoint_url: Optional[str] = None


@make_singleton
class AWSCredentials:
    def __init__(self) -> None:
        self._aws_credentials = from_config(AWSCredentialsConfig)

    @property
    def credentials(self):
        return self._aws_credentials


@overload
def make_client(
    service_name: Literal["s3"],
    aws_credentials: Optional[AWSCredentialsConfig] = None,
) -> "S3Client":
    ...


@overload
def make_client(
    service_name: Literal["sqs"],
    aws_credentials: Optional[AWSCredentialsConfig] = None,
) -> "SQSClient":
    ...


def make_client(
    service_name: Literal["s3", "sqs"],
    aws_credentials: Optional[AWSCredentialsConfig] = None,
) -> Union["S3Client", "SQSClient"]:
    aws_credentials = aws_credentials or AWSCredentials().credentials
    kwargs = {
        "region_name": aws_credentials.region_name,
        "aws_access_key_id": aws_credentials.access_key_id,
        "aws_secret_access_key": aws_credentials.secret_access_key,
    }
    if (endpoint_url := aws_credentials.endpoint_url) is not None:
        kwargs["endpoint_url"] = endpoint_url
    return Session().client(service_name, **kwargs)
