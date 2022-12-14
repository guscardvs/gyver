from contextlib import contextmanager
from contextlib import suppress
from io import BytesIO
from shutil import copyfileobj

from botocore.exceptions import ClientError
from moto.s3 import mock_s3

from gyver import boto


@contextmanager
def storage_provider():
    aws_credentials = boto.AWSCredentialsConfig(
        access_key_id="test",
        secret_access_key="",
        region_name="us-east-1",
    )
    config = boto.StorageConfig(
        bucket_name="test",
    )
    with mock_s3():
        provider = boto.StorageProvider(config, aws_credentials)
        client = provider.client
        with suppress(ClientError):
            client.head_bucket(Bucket=provider.config.bucket_name)
            client.delete_bucket(Bucket=provider.config.bucket_name)
        client.create_bucket(Bucket=provider.config.bucket_name)
        yield provider


def test_upload_file_uploads_file_correctly():
    with storage_provider() as provider:
        buffer = BytesIO("test_string".encode("utf8"))
        object_name = "name.csv"
        provider.upload_file(buffer, object_name)

        provider.client.head_object(
            Bucket=provider.config.bucket_name, Key=object_name
        )


def test_get_presigned_get_returns_url_for_object():
    with storage_provider() as provider:
        buffer = BytesIO("test_string".encode("utf8"))
        object_name = "name.csv"
        provider.upload_file(buffer, object_name)
        url = provider.generate_presigned_get(object_name)
        assert url and object_name in url


def test_is_key_returns_correctly_whether_object_exists():
    with storage_provider() as provider:
        buffer = BytesIO("test_string".encode("utf8"))
        object_name = "name.csv"
        provider.upload_file(buffer, object_name)
        assert provider.is_key("name.csv")
        assert not provider.is_key("invalid.csv")


def test_get_file_returns_readable_buffer_with_file_contents():
    with storage_provider() as provider:
        buffer = BytesIO("test_string".encode("utf8"))
        buffer_in = BytesIO()
        copyfileobj(buffer, buffer_in)
        object_name = "name.csv"
        provider.upload_file(buffer_in, object_name)

        output_buffer = provider.get_file(object_name)

        assert output_buffer.read() == buffer.read()
