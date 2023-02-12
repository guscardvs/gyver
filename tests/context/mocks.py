from gyver.context.interfaces.adapter import AtomicAdapter
from gyver.context.interfaces.adapter import AtomicAsyncAdapter


class MockClient:
    def __init__(self) -> None:
        self._active = True
        self._count = 0

    def toggle_active(self):
        self._active = not self._active

    def deactivate(self):
        self._active = False

    def increment(self):
        self._count += 1

    def decrement(self):
        self._count -= 1

    @property
    def closed(self):
        return not self._active

    @property
    def count(self):
        return self._count

    def __enter__(self):
        self.toggle_active()
        return self

    def __exit__(self, *_):
        self.toggle_active()

    async def __aenter__(self):
        self.toggle_active()
        return self

    async def __aexit__(self, *_):
        self.toggle_active()


class MockAdapter(AtomicAdapter[MockClient]):
    def is_closed(self, client: MockClient) -> bool:
        return client.closed

    def release(self, client: MockClient) -> None:
        return client.deactivate()

    def new(self) -> MockClient:
        return MockClient()

    def begin(self, client: MockClient) -> None:
        client.increment()

    def commit(self, client: MockClient) -> None:
        client.decrement()

    def rollback(self, client: MockClient) -> None:
        client.decrement()

    def in_atomic(self, client: MockClient) -> bool:
        return client.count > 0


class MockAsyncAdapter(AtomicAsyncAdapter[MockClient]):
    async def is_closed(self, client: MockClient) -> bool:
        return client.closed

    async def release(self, client: MockClient) -> None:
        client.deactivate()

    async def new(self) -> MockClient:
        return MockClient()

    async def begin(self, client: MockClient) -> None:
        client.increment()

    async def commit(self, client: MockClient) -> None:
        client.decrement()

    async def rollback(self, client: MockClient) -> None:
        client.decrement()

    async def in_atomic(self, client: MockClient) -> bool:
        return client.count > 0
