import typing

from typing_extensions import Self

T = typing.TypeVar("T")
SelfT = typing.TypeVar("SelfT")


class lazyfield(typing.Generic[SelfT, T]):
    def __init__(self, func: typing.Callable[[SelfT], T]) -> None:
        self._func = func

    def __set_name__(self, owner: type[SelfT], name: str):
        self.public_name = name
        self.private_name = f"_lazyfield_{name}"

    @typing.overload
    def __get__(self, instance: SelfT, owner: type[SelfT]) -> T:
        ...

    @typing.overload
    def __get__(
        self, instance: typing.Literal[None], owner: type[SelfT]
    ) -> Self:
        ...

    def __get__(
        self,
        instance: typing.Optional[SelfT],
        owner: typing.Optional[type[SelfT]] = None,
    ) -> typing.Union[T, Self]:
        if not instance:
            return self
        assert instance is not None
        try:
            val = typing.cast(
                T,
                object.__getattribute__(
                    instance,
                    self.private_name,
                ),
            )
        except AttributeError:
            val = self._try_set(instance)
        return val

    def _try_set(self, instance: SelfT) -> T:
        try:
            val = self._func(instance)
        except Exception as e:
            # remove exception context to create easier traceback
            raise e from None
        else:
            object.__setattr__(instance, self.private_name, val)
            return val

    def __set__(self, instance: SelfT, value: T):
        object.__setattr__(instance, self.private_name, value)

    def __delete__(self, instance: SelfT):
        object.__delattr__(instance, self.private_name)
