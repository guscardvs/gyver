# Context

[gyver.context][] is a utility designed to simplify the management of resource acquisition and sharing
within various sections of code. This utility becomes particularly advantageous when dealing with resources
that require specific enabling and disabling procedures, as well as ensuring proper handling of resource lifecycles.
Consider the following use case:

```python
class ExpensiveResource:
   
    def enable_expensive_resource(self):
        # Code to enable the expensive resource
        ...

    def is_active(self) -> bool:
        # Check if the expensive resource is currently active
        ...

    def disable_expensive_resource(self):
        # Code to disable the expensive resource
        ...

def function_a():
    resource = ExpensiveResource()
    resource.enable_expensive_resource()
    value_a = function_b(resource)
    value_b = function_c(resource)
    value_c = function_d(resource)
    resource.disable_expensive_resource()
    return value_a, value_b, value_c

def function_b(resource: ExpensiveResource):
    resource_was_active = resource.is_active()
    if not resource.is_active():
        resource.enable_expensive_resource()
    value = do_something(resource)
    if not resource_was_active:
        resource.disable_expensive_resource()
    return value

# Similar functions for function_c and function_d
```

Now, let's consider the same example with an improved approach using gyver.context:

```python
from gyver.context import Context

# First, define an adapter class that adheres to the Adapter interface

class ExpensiveResourceAdapter:
    def is_closed(self, client: ExpensiveResource):
        return not client.is_active()
    
    def release(self, client: ExpensiveResource):
        client.disable_expensive_resource()
    
    def new(self):
        client = ExpensiveResource()
        client.enable_expensive_resource()
        return client

# Utilize the adapter with gyver.context as shown below

def function_a():
    expensive_context = Context(ExpensiveResourceAdapter())
    # Within this context manager, Adapter.new is invoked,
    # and the resource is tracked until the context ends
    with expensive_context:
        value_a = function_b(expensive_context)
        value_b = function_c(expensive_context)
        value_c = function_d(expensive_context)
    # Upon context exit, context calls Adapter.release(resource)
    return value_a, value_b, value_c

# In function_b, the resource status check is no longer required.
# The resource is managed seamlessly within the context.

def function_b(context: Context[ExpensiveResource]):
    # The context manager handles resource initialization,
    # reuse, and cleanup automatically
    with context as resource:
        return do_something(resource)
```

By employing gyver.context, you streamline the management of resource acquisition and ensure proper resource handling throughout the code, resulting in cleaner, more concise, and more maintainable code.