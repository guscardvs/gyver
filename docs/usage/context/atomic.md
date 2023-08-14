# Atomicity

When working with the atomic interface provided by [gyver.context][], you can take advantage of the atomic utility function. This function simplifies the creation of atomic contexts in both synchronous and asynchronous scenarios.

## Using the `atomic` Utility Function

!!! note inline end "Asyncio"
    Note that the `atomic` function also works for the [AtomicAsyncAdapter][gyver.context]

The [atomic][gyver.context] utility function allows you to create atomic contexts with ease. It wraps a given context with the atomic interface, ensuring proper resource management and atomic operations.

Example:
```python
from gyver.context import atomic

# Create an atomic context using the atomic utility function
atomic_context = atomic(my_context)

# Inside the atomic context, the atomicity is managed automatically
with atomic_context as resource:
    # Perform operations within the atomic context
    do_something()

# Upon exiting the atomic context, the adapter's `rollback` or `commit` methods are invoked
# if any errors occurred. This happens only at the outermost frame.

```

The `atomic` function also supports an optional parameter `bound`, which determines whether the resulting context will be the owner of the resource or will attach to the current context. By default, `bound` is set to `True`, allowing reuse of already active resources from the provided context. It handles all context management from that context. When set to `False`, the new context manages resources independently, opening and closing them based on its own stack count.

Example:
```python
# Assume there's an active resource from the outer context
client = None

# Wrapping an existing context with the atomic interface
with context as client:
    pass

# Creating an atomic context that reuses the existing resource (bound=True)
with atomic(context) as atomic_client:
    print(atomic_client is client)  # True

# Creating an independent atomic context with its own resource (bound=False)
with atomic(context, bound=False) as unbound_client:
    print(unbound_client is client)  # False

```