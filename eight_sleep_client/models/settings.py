"""Base class for dict-backed settings objects.

Subclasses declare fields as type annotations. The metaclass
auto-generates properties that read from the underlying dict,
converting snake_case field names to camelCase keys.
"""

from __future__ import annotations

import sys
from typing import Any, Generic, TypeVar, overload

from ..utils import camel_to_snake, snake_to_camel

T = TypeVar("T")


# Must be defined before Settings, which references it as its metaclass.
class _SettingsMeta(type):
    def __new__(mcs, name, bases, namespace, **_kwargs):
        cls = super().__new__(mcs, name, bases, namespace)
        if name == "Settings":
            return cls
        for field_name in namespace.get("__annotations__", {}):
            if field_name.startswith("_"):
                continue
            camel_key = snake_to_camel(field_name)
            setattr(cls, field_name, property(lambda self, k=camel_key: self._data[k]))
        return cls


class Settings(metaclass=_SettingsMeta):
    """Base class for dict-backed settings objects."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data


class settings_property(Generic[T]):
    """Descriptor that wraps a nested dict key in a Settings subclass.

    Uses a string class name for lazy resolution, allowing the settings
    class to be defined after the model that references it.
    """

    def __init__(self, cls_name: str) -> None:
        self._cls_name = cls_name

    @overload
    def __get__(self, obj: None, objtype: type) -> settings_property[T]: ...
    @overload
    def __get__(self, obj: Any, objtype: type) -> T: ...

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        stripped = self._cls_name.removeprefix(objtype.__name__).removesuffix("Settings")
        key = camel_to_snake(stripped)
        module = sys.modules[objtype.__module__]
        cls = getattr(module, self._cls_name)
        return cls(obj._data[key])
