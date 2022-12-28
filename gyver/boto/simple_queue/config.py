from gyver.config import ProviderConfig


class QueueConfig(ProviderConfig):
    __prefix__ = "queue"

    name: str
    message_batch_limit: int = 10
    visibility_timeout: int = 10
    wait_time_seconds: int = 3
    stream_sleep_seconds: float = 0.1
