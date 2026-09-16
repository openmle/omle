"""Internal serialization helpers shared by all IR classes."""

from __future__ import annotations

import base64
from enum import Enum
from typing import Any


def _to_dict_value(v: Any) -> Any:
    """Convert a single value to a JSON-safe dict representation."""
    if v is None:
        return None
    if isinstance(v, Enum):
        return v.name
    if isinstance(v, bytes):
        return base64.b64encode(v).decode("ascii")
    if isinstance(v, list):
        return [_to_dict_value(item) for item in v]
    if isinstance(v, dict):
        return {k: _to_dict_value(val) for k, val in v.items()}
    if hasattr(v, "to_dict"):
        return v.to_dict()
    return v


def obj_to_dict(obj: Any) -> dict[str, Any]:
    """Convert a dataclass instance to a dict, omitting None and empty-list fields."""
    result: dict[str, Any] = {}
    for field_name, field_val in vars(obj).items():
        if field_val is None:
            continue
        if isinstance(field_val, list) and len(field_val) == 0:
            continue
        if isinstance(field_val, dict) and len(field_val) == 0:
            continue
        result[field_name] = _to_dict_value(field_val)
    return result


def enum_from_dict(cls: type[Enum], value: Any) -> Enum:
    """Parse an enum from a string name or integer value."""
    if value is None:
        return list(cls)[0]  # default (zero value)
    if isinstance(value, cls):
        return value
    if isinstance(value, str):
        return cls[value]
    if isinstance(value, int):
        return cls(value)
    raise ValueError(f"Cannot parse {cls.__name__} from {value!r}")


def bytes_from_dict(value: Any) -> bytes | None:
    """Decode a base64 string to bytes."""
    if value is None:
        return None
    if isinstance(value, bytes):
        return value
    return base64.b64decode(value)

def ints_from_dict(value: Any) -> list[int]:
    """Return a list of ints from a JSON-decoded repeated int64 field.

    Protobuf's canonical JSON mapping encodes 64-bit integers as **strings**, so
    a value that round-tripped through ``MessageToJson`` arrives as ``["-1", "2"]``
    rather than ``[-1, 2]``. Coerce here so the IR always holds ints and can be
    re-serialized.
    """
    if not value:
        return []
    return [int(v) for v in value]


def int_from_dict(value: Any, default: int = 0) -> int:
    """Return an int from a JSON-decoded int64 field (see ``ints_from_dict``)."""
    if value is None or value == "":
        return default
    return int(value)
