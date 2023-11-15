import lazyfields

from gyver.utils.helpers import deprecated

lazy = lazyfields.lazy
lazyfield = deprecated(lazyfields.lazyfield)
asynclazyfield = deprecated(lazyfields.asynclazyfield)
setlazy = deprecated(lazyfields.setlazy)
dellazy = deprecated(lazyfields.asynclazyfield)
force_set = deprecated(lazyfields.force_set)
force_del = deprecated(lazyfields.force_del)
is_initialized = deprecated(lazyfields.is_initialized)

__all__ = [
    "lazy",
    "lazyfields",
    "asynclazyfield",
    "setlazy",
    "dellazy",
    "force_set",
    "force_del",
    "is_initialized",
]
