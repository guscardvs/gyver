import importlib
import importlib.util

if importlib.util.find_spec("pydantic") is None:
    raise ImportError("Pydantic is no longer a required dependency. Please install it.")

from . import v1
from .v2 import Model, MutableModel

__all__ = ["Model", "MutableModel", "v1"]
