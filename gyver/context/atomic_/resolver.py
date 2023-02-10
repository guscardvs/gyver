from typing import Union
from typing import overload

from gyver.context.context import AsyncContext
from gyver.context.context import Context
from gyver.context.typedef import T

from .bound import AsyncBoundContext
from .bound import BoundContext
from .core import AsyncAtomicContext
from .core import AtomicContext


@overload
def atomic(context: Context[T], bound: bool = True) -> AtomicContext[T]:
    ...


@overload
def atomic(context: AsyncContext[T], bound: bool = True) -> AsyncAtomicContext[T]:
    ...


def atomic(
    context: Union[Context[T], AsyncContext[T]], bound: bool = True
) -> Union[Context[T], AsyncContext[T]]:
    required_methods = {"begin", "commit", "rollback", "in_atomic"}
    adapter_methods = set(dir(context.adapter))

    if not required_methods.issubset(adapter_methods):
        raise ValueError(
            f"The adapter does not have required methods {required_methods}"
        )

    if bound:
        return (
            BoundContext(context.adapter, context)  # type: ignore
            if isinstance(context, Context)
            else AsyncBoundContext(context.adapter, context)  # type: ignore
        )

    return (
        AtomicContext(context.adapter)  # type: ignore
        if isinstance(context, Context)
        else AsyncAtomicContext(context.adapter)  # type: ignore
    )
