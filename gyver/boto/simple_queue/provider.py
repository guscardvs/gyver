import time
from typing import Any
from typing import Callable
from typing import Generator
from typing import Generic
from typing import Optional
from typing import TypeVar

from botocore.exceptions import ClientError

from gyver.boto.base import AWSCredentials
from gyver.boto.base import AWSCredentialsConfig
from gyver.boto.base import make_client
from gyver.config import from_config
from gyver.exc import QueueNotFound
from gyver.utils import lazyfield
from gyver.utils import panic

from .config import QueueConfig
from .models import Message
from .models import Messages
from .models import MessageWrapper

T = TypeVar("T")


class QueueProvider:
    def __init__(
        self,
        config: Optional[QueueConfig] = None,
        aws_credentials: Optional[AWSCredentialsConfig] = None,
    ) -> None:
        self._config = config or from_config(QueueConfig)
        self._aws_credentials = aws_credentials

    @lazyfield
    def client(self):
        return make_client("sqs", self._aws_credentials)

    @property
    def config(self):
        return self._config

    @property
    def aws_credentials(self):
        return self._aws_credentials or AWSCredentials()

    @lazyfield
    def queue_url(self):
        try:
            queue_url = self.client.get_queue_url(QueueName=self._config.name)
        except ClientError:
            raise panic(
                QueueNotFound,
                f"{self._config.name} does not exist on given credentials",
            ) from None
        else:
            return queue_url["QueueUrl"]

    def get_messages(self):
        response = self.client.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=self._config.message_batch_limit,
            VisibilityTimeout=self._config.visibility_timeout,
            WaitTimeSeconds=self._config.wait_time_seconds,
        )
        return Messages.parse_obj(response)

    def send_message(self, body: str, **kwargs: Any):
        self.client.send_message(QueueUrl=self.queue_url, MessageBody=body, **kwargs)

    def stream(
        self,
        cast: Callable[[Message], T] = MessageWrapper,
        max_rounds: int = 0,
    ) -> "QueueStream[T]":
        return QueueStream(self, cast, max_rounds)


class QueueStream(Generic[T]):
    def __init__(
        self,
        provider: QueueProvider,
        cast: Callable[[Message], T],
        max_rounds: int,
    ) -> None:
        self._internal_provider = provider
        self._cast = cast
        self._max_rounds = max_rounds

    def _iter(self) -> Generator[T, None, None]:
        counter = 0
        while True:
            message_response = self._internal_provider.get_messages()
            yield from (self._cast(item) for item in message_response.messages)
            time.sleep(self._internal_provider.config.stream_sleep_seconds)
            counter += 1
            if self._max_rounds > 0 and self._max_rounds == counter:
                break

    def __iter__(self):
        yield from self._iter()
