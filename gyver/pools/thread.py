import threading
from queue import Empty
from queue import LifoQueue
from queue import Queue
from time import time
from collections.abc import Callable
from typing import Generic
from typing import TypeVar

from gyver.attrs import call_init
from gyver.attrs import mutable

from gyver.exc import ErrorGroup

from .resource import Resource

T = TypeVar("T")


FactoryType = Callable[[], T]
ReleaserType = Callable[[T], None]


@mutable
class ThreadPool(Generic[T]):
    resources: Queue[Resource[T]]
    factory: FactoryType[T]
    releaser: ReleaserType[T]
    _pool_recycle: float
    _pool_size: int
    _available: int
    _available_semaphore: threading.Lock

    def __init__(
        self,
        factory: FactoryType[T],
        releaser: ReleaserType[T],
        queue_class: type[Queue] = LifoQueue,
        pool_size: int = 10,
        pool_recycle: float = 3600,
    ):
        call_init(
            self,
            resources=queue_class(pool_size),
            factory=factory,
            releaser=releaser,
            pool_recycle=pool_recycle,
            pool_size=pool_size,
            available=pool_size,
            available_semaphore=threading.Lock(),
        )

    def _initialize_resource(self) -> Resource[T]:
        resource = self.factory()
        return Resource.from_now(resource)

    def _maybe_recycle(self, resource: Resource[T], current: float | None = None) -> T:
        current = current or time()
        if (
            self._pool_recycle >= 0
            and resource.last_usage + self._pool_recycle <= current
        ):
            self.releaser(resource.get())
            resource = self._initialize_resource()
        return resource.get()

    def acquire(self) -> T:
        if self._decrease_available():
            try:
                resource = self.resources.get_nowait()
            except Empty:
                resource = self._initialize_resource()
        else:
            resource = self.resources.get()
        return self._maybe_recycle(resource)

    def release(self, resource: T) -> None:
        self.resources.put_nowait(Resource.from_resource(resource))
        self._increase_available()

    def prefill(self, count: int | None = None) -> None:
        count = count or self._pool_size
        count = min(count, self._pool_size)

        while self.resources.qsize() < count:
            resource = self._initialize_resource()
            self.resources.put_nowait(resource)
            self._decrease_available()

    def dispose(self) -> None:
        errors = []
        while not self.resources.empty():
            resource = self.resources.get()
            try:
                self.releaser(resource.get())
            except Exception as e:
                errors.append(e)
            self._decrease_available()
        if errors:
            raise ErrorGroup("Could not kill all resources", *errors)

    def _decrease_available(self):
        """
        Decrease the count of available resources.

        This method should not be called directly. It is used internally
        by the `acquire` and `dispose` methods to keep track of the number
        of available resources.
        """
        with self._available_semaphore:
            if self._available == 0:
                return False
            self._available -= 1
            return True

    def _increase_available(self):
        """
        Increase the count of available resources.

        This method should not be called directly. It is used internally by the
        `release` and `prefill` methods to keep track of the number
        of available resources.
        """
        with self._available_semaphore:
            if self._available == self._pool_size:
                return False
            self._available += 1
            return True
