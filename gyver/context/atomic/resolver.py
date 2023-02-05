from gyver.context.context import Context, AsyncContext
from .bound import BoundContext, AsyncBoundContext
from .core import AsyncAtomicContext, AtomicContext
from typing import Union, overload
from gyver.context.typedef import T


@overload
def in_atomic(context: Context[T], bound: bool = True) -> AtomicContext[T]:
    ...


@overload
def in_atomic(
    context: AsyncContext[T], bound: bool = True
) -> AsyncAtomicContext[T]:
    ...


def in_atomic(
    context: Union[Context[T], AsyncContext[T]], bound: bool = True
) -> Union[AtomicContext[T], AsyncAtomicContext[T]]:
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
