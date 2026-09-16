"""Load and save OMLE models.

Supported formats:
  - JSON (.json) — human-readable, no dependencies
  - Protobuf binary (.omle, .pb) — compact binary, requires protobuf package

Usage::

    import omle

    model = omle.load("model.json")
    omle.save(model, "model.json")

    model = omle.load("model.omle")    # protobuf binary
    omle.save(model, "model.omle")
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Union

from .ir.model import OMLEModel

PathLike = Union[str, os.PathLike]


# ── JSON ──────────────────────────────────────────────────────────────────────

def load_json(path: PathLike) -> OMLEModel:
    """Load an OMLE model from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    return OMLEModel.from_dict(d)


def save_json(model: OMLEModel, path: PathLike, *, indent: int = 2) -> None:
    """Save an OMLE model to a JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(model.to_dict(), f, indent=indent, ensure_ascii=False)


def to_json(model: OMLEModel, *, indent: int = 2) -> str:
    """Serialize an OMLE model to a JSON string."""
    return json.dumps(model.to_dict(), indent=indent, ensure_ascii=False)


def from_json(text: str) -> OMLEModel:
    """Deserialize an OMLE model from a JSON string."""
    return OMLEModel.from_dict(json.loads(text))


# ── Protobuf ──────────────────────────────────────────────────────────────────

def load_proto(path: PathLike) -> OMLEModel:
    """Load an OMLE model from a protobuf binary file.

    Requires the ``protobuf`` package and generated ``omle_pb2`` module.
    Run ``scripts/gen_proto.sh`` to generate the pb2 module first.
    """
    from .proto.convert import get_pb2, proto_to_ir

    pb2 = get_pb2()
    msg = pb2.OMLEModel()
    with open(path, "rb") as f:
        msg.ParseFromString(f.read())
    return proto_to_ir(msg)


def save_proto(model: OMLEModel, path: PathLike) -> None:
    """Save an OMLE model to a protobuf binary file."""
    from .proto.convert import ir_to_proto

    msg = ir_to_proto(model)
    with open(path, "wb") as f:
        f.write(msg.SerializeToString())


def to_proto_bytes(model: OMLEModel) -> bytes:
    """Serialize an OMLE model to protobuf binary bytes."""
    from .proto.convert import ir_to_proto

    return ir_to_proto(model).SerializeToString()


def from_proto_bytes(data: bytes) -> OMLEModel:
    """Deserialize an OMLE model from protobuf binary bytes."""
    from .proto.convert import get_pb2, proto_to_ir

    pb2 = get_pb2()
    msg = pb2.OMLEModel()
    msg.ParseFromString(data)
    return proto_to_ir(msg)


# ── Auto-dispatch ─────────────────────────────────────────────────────────────

_PROTO_EXTENSIONS = {".omle", ".pb", ".bin"}
_JSON_EXTENSIONS = {".json"}


def load(path: PathLike) -> OMLEModel:
    """Load an OMLE model, auto-detecting format from file extension.

    - ``.json`` → JSON
    - ``.omle``, ``.pb``, ``.bin`` → protobuf binary
    """
    ext = Path(path).suffix.lower()
    if ext in _JSON_EXTENSIONS:
        return load_json(path)
    if ext in _PROTO_EXTENSIONS:
        return load_proto(path)
    raise ValueError(
        f"Cannot determine file format from extension {ext!r}. "
        "Use load_json() or load_proto() directly."
    )


def save(model: OMLEModel, path: PathLike, **kwargs) -> None:
    """Save an OMLE model, auto-detecting format from file extension."""
    ext = Path(path).suffix.lower()
    if ext in _JSON_EXTENSIONS:
        save_json(model, path, **kwargs)
        return
    if ext in _PROTO_EXTENSIONS:
        save_proto(model, path)
        return
    raise ValueError(
        f"Cannot determine file format from extension {ext!r}. "
        "Use save_json() or save_proto() directly."
    )
