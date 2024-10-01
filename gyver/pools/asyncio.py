import asyncio
from time import time
from typing import Any
from collections.abc import Callable
from collections.abc import Coroutine
from typing import Generic
from typing import TypeVar

from gyver.attrs import call_init
from gyver.attrs import mutable

from gyver.exc import ErrorGroup

from .resource import Resource

T = TypeVar("T")


FactoryType = Callable[[], Coroutine[Any, Any, T]]
ReleaserType = Callable[[T], Coroutine[Any, Any, None]]


@mutable
class AsyncPool(Generic[T]):
    resources: asyncio.Queue[Resource[T]]
    factory: FactoryType[T]
    releaser: ReleaserType[T]
    _pool_recycle: float
    _pool_size: int
    _available: int
    _available_semaphore: asyncio.Lock

    def __init__(
        self,
        factory: FactoryType[T],
        releaser: ReleaserType[T],
        queue_class: type[asyncio.Queue[T]] = asyncio.LifoQueue,
        pool_size: int = 10,
        pool_recycle: float = 3600,
    ):
        """
        Initialize the AsyncPool.

        :param factory: A coroutine function that creates a new resource.
        :param releaser: A coroutine function that releases a resource.
        :param queue_class: The class to use for the resources queue. Defaults to asyncio.LifoQueue.
        :param pool_size: The maximum size of the resource pool. Defaults to 10.
        :param pool_recycle: The time in seconds after which a resource is considered expired and should be recycled. Defaults to 3600 (1 hour).
        """
        call_init(
            self,
            resources=queue_class(pool_size),
            factory=factory,
            releaser=releaser,
            pool_recycle=pool_recycle,
            pool_size=pool_size,
            available=pool_size,
            available_semaphore=asyncio.Lock(),
        )

    async def _initialize_resource(self) -> Resource[T]:
        """Creates a resource from the factory and returns it wrapped in the Resource object
        :return: The Resource wrapper
        """
        resource = await self.factory()
        return Resource.from_now(resource)

    async def _maybe_recycle(
        self, resource: Resource[T], current_ts: float | None = None
    ) -> T:
        """Returns resource from resource object or
        releases the current resource and returns a new one if
        resource is expired.

        :param resource: The resource wrapper to be "maybe" recycled.
        :param current_ts: timestamp, defaults to `time.time()`

        :return: The resource acquired.
        """
        current_ts = current_ts or time()
        if (
            self._pool_recycle > 0
            and resource.last_usage + self._pool_recycle <= current_ts
        ):
            await self.releaser(resource.get())
            resource = await self._initialize_resource()
        return resource.get()

    async def acquire(self) -> T:
        """
        Acquires a resource from the pool, waiting until available.

        :return: T
        """
        acquired = await self._decrease_available()
        if not acquired:
            resource = await self.resources.get()
        else:
            try:
                resource = self.resources.get_nowait()
            except asyncio.QueueEmpty:
                resource = await self._initialize_resource()
        return await self._maybe_recycle(resource)

    async def release(self, resource: T) -> None:
        """Puts resource back in queue and increases the
        amount of resources available to be acquired

        :param resource: The resource to be put.
        :return: None
        """
        self.resources.put_nowait(Resource.from_resource(resource))
        await self._increase_available()

    async def prefill(self, count: int | None = None) -> None:
        """
        Prefills the queue by the amount passed.

        :param count: The amount of resources to initialize, up to the
            `pool_size`. Defaults to the pool_size if None.
        """
        count = count or self._pool_size
        count = min(count, self._pool_size)

        while self.resources.qsize() < count and await self._decrease_available():
            resource = await self._initialize_resource()
            self.resources.put_nowait(resource)

    async def dispose(self) -> None:
        """
        Remove and release all items of from the queue.

        :return: None
        :raises: ErrorGroup if any error happened while closing
        """
        errors = []
        while not self.resources.empty():
            resource = await self.resources.get()
            try:
                await self.releaser(resource.get())
            except Exception as e:
                errors.append(e)
            await self._decrease_available()
        if errors:
            raise ErrorGroup("Could not kill all resources", *errors)

    async def _decrease_available(self):
        """
        Decrease the count of available resources.

        This method should not be called directly. It is used internally
        by the `acquire` and `dispose` methods to keep track of the number
        of available resources.
        """
        async with self._available_semaphore:
            if self._available == 0:
                return False
            self._available -= 1
            return True

    async def _increase_available(self):
        """
        Increase the count of available resources.

        This method should not be called directly. It is used internally by the
        `release` and `prefill` methods to keep track of the number
        of available resources.
        """
        async with self._available_semaphore:
            if self._available == self._pool_size:
                return False
            self._available += 1
            return True
