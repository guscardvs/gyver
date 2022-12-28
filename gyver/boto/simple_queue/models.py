from contextlib import suppress
from typing import Any

from orjson import JSONDecodeError

from gyver.boto.models import BotoModel
from gyver.utils import json


class Message(BotoModel):
    message_id: str
    receipt_handle: str
    body: str


class Messages(BotoModel):
    messages: list[Message]
    response_metadata: dict[str, Any]


class MessageWrapper:
    def __init__(self, message: Message) -> None:
        self._message = message

    def get(self):
        return self._message

    def loads(self):
        with suppress(JSONDecodeError):
            return json.loads(self._message.body)
