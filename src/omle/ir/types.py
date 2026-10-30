"""Scalar, TensorType, and TensorRef IR classes."""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from ._util import enum_from_dict, int_from_dict, ints_from_dict, obj_to_dict
from .enums import DataType

if TYPE_CHECKING:  # circular at runtime: .tensor imports this module
    from .tensor import SparseTensor, Tensor


@dataclass
class Scalar:
    """Canonical scalar literal value (proto oneof: bool/int/float32/float64/string)."""

    bool_value: Optional[bool] = None
    int_value: Optional[int] = None
    float_value: Optional[float] = None
    double_value: Optional[float] = None
    string_value: Optional[str] = None

    def __post_init__(self) -> None:
        set_fields = sum(
            1
            for v in (self.bool_value, self.int_value, self.float_value,
                      self.double_value, self.string_value)
            if v is not None
        )
        if set_fields > 1:
            raise ValueError("Scalar: only one value field may be set at a time")

    # ── convenience constructors ──────────────────────────────────────────────

    @classmethod
    def bool(cls, v: bool) -> "Scalar":
        return cls(bool_value=v)

    @classmethod
    def int(cls, v: int) -> "Scalar":
        return cls(int_value=v)

    @classmethod
    def float(cls, v: float) -> "Scalar":
        return cls(double_value=v)

    @classmethod
    def float32(cls, v: float) -> "Scalar":
        return cls(float_value=v)

    @classmethod
    def string(cls, v: str) -> "Scalar":
        return cls(string_value=v)

    @property
    def value(self):
        """Return the Python value regardless of which field is set."""
        if self.bool_value is not None:
            return self.bool_value
        if self.int_value is not None:
            return self.int_value
        if self.float_value is not None:
            return self.float_value
        if self.double_value is not None:
            return self.double_value
        return self.string_value

    def to_dict(self) -> dict:
        d = obj_to_dict(self)
        if "float_value" in d:
            d["float_value"] = struct.unpack("f", struct.pack("f", d["float_value"]))[0]
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Scalar":
        return cls(
            bool_value=d.get("bool_value"),
            int_value=(int_from_dict(d["int_value"]) if "int_value" in d else None),
            float_value=d.get("float_value"),
            double_value=d.get("double_value"),
            string_value=d.get("string_value"),
        )


@dataclass
class TensorType:
    """Tensor element type and shape declaration."""

    dtype: DataType = DataType.DATA_TYPE_UNSPECIFIED
    shape: list[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "TensorType":
        return cls(
            dtype=enum_from_dict(DataType, d.get("dtype")),
            shape=ints_from_dict(d.get("shape")),
        )


@dataclass
class TensorRef:
    """Reference to a TensorEntry by its id."""

    id: str = ""

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "TensorRef":
        return cls(id=d.get("id", ""))


@dataclass
class TensorValue:
    """Wraps a model parameter tensor: inline dense, inline sparse, or a TensorRef.

    Mirrors the proto TensorValue oneof (tensor / sparse / tensor_ref).
    Only one field should be set.
    """

    tensor: Optional["Tensor"] = None
    sparse: Optional["SparseTensor"] = None
    tensor_ref: Optional["TensorRef"] = None

    def to_dict(self) -> dict:
        if self.tensor is not None:
            return {"tensor": self.tensor.to_dict()}
        if self.sparse is not None:
            return {"sparse": self.sparse.to_dict()}
        if self.tensor_ref is not None:
            return {"tensor_ref": self.tensor_ref.to_dict()}
        return {}

    @classmethod
    def from_dict(cls, d: dict) -> "TensorValue":
        from .tensor import SparseTensor, Tensor
        if not d:
            return cls()
        if "tensor" in d:
            return cls(tensor=Tensor.from_dict(d["tensor"]))
        if "sparse" in d:
            return cls(sparse=SparseTensor.from_dict(d["sparse"]))
        if "tensor_ref" in d:
            return cls(tensor_ref=TensorRef.from_dict(d["tensor_ref"]))
        return cls()

    @classmethod
    def of_tensor(cls, t: "Tensor") -> "TensorValue":
        return cls(tensor=t)

    @classmethod
    def of_ref(cls, ref: "TensorRef") -> "TensorValue":
        return cls(tensor_ref=ref)

    @classmethod
    def of_sparse(cls, s: "SparseTensor") -> "TensorValue":
        return cls(sparse=s)


@dataclass(eq=False)
class NameRef:
    """Reference to a named value, or to one named field within that value."""

    value: str = ""
    field: str = ""

    def __eq__(self, other: object) -> bool:
        if isinstance(other, NameRef):
            return self.value == other.value and self.field == other.field
        if isinstance(other, str):
            return self.value == other and not self.field
        return NotImplemented

    def __hash__(self) -> int:
        # When field is empty, hash must equal hash(value) so that
        # NameRef("x", "") == "x" implies hash(NameRef("x", "")) == hash("x").
        if not self.field:
            return hash(self.value)
        return hash((self.value, self.field))

    def to_dict(self) -> dict:
        d: dict = {"value": self.value}
        if self.field:
            d["field"] = self.field
        return d

    @classmethod
    def from_dict(cls, d) -> "NameRef":
        if isinstance(d, str):
            return cls(value=d)
        if isinstance(d, dict):
            return cls(
                value=d.get("value", ""),
                field=d.get("field", ""),
            )
        return cls()
