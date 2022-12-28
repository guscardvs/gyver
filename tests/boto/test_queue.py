from contextlib import contextmanager
from contextlib import suppress

from moto.sqs import mock_sqs

from gyver import boto
from gyver.exc import QueueNotFound
from gyver.utils import json


@contextmanager
def queue_provider():
    aws_credentials = boto.AWSCredentialsConfig(
        access_key_id="test",
        secret_access_key="",
        region_name="us-east-1",
    )
    config = boto.QueueConfig(
        name="test",
    )
    with mock_sqs():
        provider = boto.QueueProvider(config, aws_credentials)
        client = provider.client
        with suppress(QueueNotFound):
            queue_url = provider.queue_url
            client.delete_queue(QueueUrl=queue_url)
        client.create_queue(QueueName=provider.config.name)
        yield provider


def test_send_message_puts_message_in_queue():
    with queue_provider() as provider:
        expected = {"user_id": 1}
        provider.send_message(json.dumps(expected))
        client = provider.client
        messages = client.receive_message(QueueUrl=provider.queue_url)
        (message,) = messages["Messages"]
        assert json.loads(message["Body"]) == expected


def test_get_message_returns_list_of_messages():
    with queue_provider() as provider:
        expected = {"user_id": 1}
        provider.send_message(json.dumps(expected))
        response = provider.get_messages()
        (message,) = response.messages
        assert json.loads(message.body) == expected


def test_queue_stream_iterates_over_messages():
    with queue_provider() as provider:
        expected = {"user_id": 1}
        provider.send_message(json.dumps(expected))
        stream = provider.stream(max_rounds=1)
        for message in stream:
            assert message.loads() == expected
