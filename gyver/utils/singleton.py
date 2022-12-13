import typing

T = typing.TypeVar("T")


def make_singleton(cls: type[T]) -> type[T]:
    instance = None
    init_called = False
    cls_new = cls.__new__
    cls_init = cls.__init__

    def custom_new(*args, **kwds) -> T:
        nonlocal instance
        if instance is None:
            new_instance = (
                object.__new__(cls)
                if cls_new is object.__new__
                else cls_new(*args, **kwds)
            )
            instance = new_instance
        return instance

    def custom_init(*args, **kwds):
        nonlocal init_called
        if not init_called:
            cls_init(*args, **kwds)
            init_called = True

    cls.__new__ = custom_new  # type: ignore
    cls.__init__ = custom_init

    return cls
