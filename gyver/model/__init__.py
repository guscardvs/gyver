try:
    from .v2 import Model, MutableModel
    is_v2 = True
except ImportError:
    from .v1 import Model, MutableModel
    is_v2 = False

__all__ = ["Model", "MutableModel", "is_v2"]
