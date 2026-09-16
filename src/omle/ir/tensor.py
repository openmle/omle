"""Dense tensor, sparse tensor, and constant IR classes."""

from __future__ import annotations

import base64
import struct
from dataclasses import dataclass, field
from typing import Optional

from ._util import bytes_from_dict, ints_from_dict
from .types import Scalar, TensorType


def _unwrap(d: dict, key: str) -> list:
    """Extract a list from either flat IR JSON format or proto JSON wrapper format.

    IR JSON:    ``{"float32_data": [1.0, 2.0]}``
    Proto JSON: ``{"float32_data": {"values": [1.0, 2.0]}}``
    """
    val = d.get(key)
    if val is None:
        return []
    if isinstance(val, dict):
        return list(val.get("values", []))
    return list(val)


@dataclass
class Tensor:
    """Dense tensor value with typed payload storage.

    Exactly one data field should be populated at a time, mirroring the
    ``oneof data`` constraint in the proto schema.
    """

    name: str = ""
    type: Optional[TensorType] = None
    raw_data: Optional[bytes] = None
    float32_data: list[float] = field(default_factory=list)
    float64_data: list[float] = field(default_factory=list)
    int32_data: list[int] = field(default_factory=list)
    int64_data: list[int] = field(default_factory=list)
    string_data: list[str] = field(default_factory=list)
    bytes_data: list[bytes] = field(default_factory=list)
    bool_data: list[bool] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = {}
        if self.name:
            d["name"] = self.name
        if self.type is not None:
            d["type"] = self.type.to_dict()
        if self.raw_data is not None:
            d["raw_data"] = base64.b64encode(self.raw_data).decode("ascii")
        if self.float32_data:
            # Normalise to canonical float64 representations of float32 bit patterns
            # so that JSON and proto binary are consistent (both reflect the same bits).
            d["float32_data"] = [struct.unpack("f", struct.pack("f", x))[0]
                                  for x in self.float32_data]
        for key in ("float64_data", "int32_data", "int64_data", "string_data", "bool_data"):
            val = getattr(self, key)
            if val:
                d[key] = list(val)
        if self.bytes_data:
            d["bytes_data"] = [base64.b64encode(b).decode("ascii") for b in self.bytes_data]
        if self.attributes:
            d["attributes"] = dict(self.attributes)
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Tensor":
        raw = d.get("raw_data")
        bytes_data_raw = _unwrap(d, "bytes_data")
        return cls(
            name=d.get("name", ""),
            type=TensorType.from_dict(d["type"]) if "type" in d else None,
            raw_data=bytes_from_dict(raw) if raw is not None else None,
            float32_data=_unwrap(d, "float32_data"),
            float64_data=_unwrap(d, "float64_data"),
            int32_data=_unwrap(d, "int32_data"),
            int64_data=ints_from_dict(_unwrap(d, "int64_data")),
            string_data=_unwrap(d, "string_data"),
            bytes_data=[base64.b64decode(b) for b in bytes_data_raw],
            bool_data=_unwrap(d, "bool_data"),
            attributes=dict(d.get("attributes", {})),
        )


# ── Sparse tensor ─────────────────────────────────────────────────────────────

@dataclass
class CSRMatrix:
    """Compressed Sparse Row matrix storage for a rank-2 sparse tensor.

    Exactly one data field should be populated at a time, mirroring the
    ``oneof data`` constraint in the proto schema.
    """

    indices: list[int] = field(default_factory=list)
    indptr: list[int] = field(default_factory=list)
    raw_data: Optional[bytes] = None
    float32_data: list[float] = field(default_factory=list)
    float64_data: list[float] = field(default_factory=list)
    int32_data: list[int] = field(default_factory=list)
    int64_data: list[int] = field(default_factory=list)
    string_data: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d: dict = {}
        if self.indices:
            d["indices"] = list(self.indices)
        if self.indptr:
            d["indptr"] = list(self.indptr)
        if self.raw_data is not None:
            d["raw_data"] = base64.b64encode(self.raw_data).decode("ascii")
        for key in ("float32_data", "float64_data", "int32_data", "int64_data", "string_data"):
            val = getattr(self, key)
            if val:
                d[key] = list(val)
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "CSRMatrix":
        raw = d.get("raw_data")
        return cls(
            indices=_unwrap(d, "indices"),
            indptr=_unwrap(d, "indptr"),
            raw_data=base64.b64decode(raw) if raw is not None else None,
            float32_data=_unwrap(d, "float32_data"),
            float64_data=_unwrap(d, "float64_data"),
            int32_data=_unwrap(d, "int32_data"),
            int64_data=ints_from_dict(_unwrap(d, "int64_data")),
            string_data=_unwrap(d, "string_data"),
        )


@dataclass
class SparseTensor:
    """Sparse tensor value (CSR format, rank-2 only in v1)."""

    name: str = ""
    type: Optional[TensorType] = None
    default_value: Optional[Scalar] = None
    csr: Optional[CSRMatrix] = None
    attributes: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d: dict = {}
        if self.name:
            d["name"] = self.name
        if self.type is not None:
            d["type"] = self.type.to_dict()
        if self.default_value is not None:
            d["default_value"] = self.default_value.to_dict()
        if self.csr is not None:
            d["csr"] = self.csr.to_dict()
        if self.attributes:
            d["attributes"] = dict(self.attributes)
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "SparseTensor":
        from .types import Scalar  # local import avoids circular dependency
        return cls(
            name=d.get("name", ""),
            type=TensorType.from_dict(d["type"]) if "type" in d else None,
            default_value=Scalar.from_dict(d["default_value"])
                if "default_value" in d else None,
            csr=CSRMatrix.from_dict(d["csr"]) if "csr" in d else None,
            attributes=dict(d.get("attributes", {})),
        )


# ── TensorEntry ───────────────────────────────────────────────────────────────

@dataclass
class TensorEntry:
    """Named model tensor entry wrapping a dense or sparse tensor.

    ``id`` is the unique lookup key referenced by ``TensorRef.id``.
    """

    id: str = ""
    dense: Optional[Tensor] = None
    sparse: Optional[SparseTensor] = None
    attributes: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d: dict = {}
        if self.id:
            d["id"] = self.id
        if self.dense is not None:
            d["dense"] = self.dense.to_dict()
        elif self.sparse is not None:
            d["sparse"] = self.sparse.to_dict()
        if self.attributes:
            d["attributes"] = dict(self.attributes)
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "TensorEntry":
        return cls(
            id=d.get("id", ""),
            dense=Tensor.from_dict(d["dense"]) if "dense" in d else None,
            sparse=SparseTensor.from_dict(d["sparse"]) if "sparse" in d else None,
            attributes=dict(d.get("attributes", {})),
        )
