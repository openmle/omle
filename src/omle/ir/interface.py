"""InputSpec, OutputSpec, and OutputBinding IR classes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from ._util import enum_from_dict, obj_to_dict
from .enums import OutputRole
from .types import Scalar, TensorType


@dataclass
class OutputBinding:
    """Semantic binding for a model or node output."""

    target_name: str = ""
    values: list[Scalar] = field(default_factory=list)
    segment_id: str = ""
    rank: int = 0
    attributes: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "OutputBinding":
        return cls(
            target_name=d.get("target_name", ""),
            values=[Scalar.from_dict(v) for v in d.get("values", [])],
            segment_id=d.get("segment_id", ""),
            rank=d.get("rank", 0),
            attributes=dict(d.get("attributes", {})),
        )


@dataclass
class InputSpec:
    """Declares one external input of the model inference interface."""

    name: str = ""
    type: Optional[TensorType] = None
    description: str = ""
    attributes: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "InputSpec":
        return cls(
            name=d.get("name", ""),
            type=TensorType.from_dict(d["type"]) if "type" in d else None,
            description=d.get("description", ""),
            attributes=dict(d.get("attributes", {})),
        )


@dataclass
class OutputSpec:
    """Declares one external output of the model inference interface."""

    name: str = ""
    type: Optional[TensorType] = None
    role: OutputRole = OutputRole.OUTPUT_ROLE_UNSPECIFIED
    binding: Optional[OutputBinding] = None
    description: str = ""
    field_names: list[str] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "OutputSpec":
        return cls(
            name=d.get("name", ""),
            type=TensorType.from_dict(d["type"]) if "type" in d else None,
            role=enum_from_dict(OutputRole, d.get("role")),
            binding=OutputBinding.from_dict(d["binding"]) if "binding" in d else None,
            description=d.get("description", ""),
            field_names=list(d.get("field_names", [])),
            attributes=dict(d.get("attributes", {})),
        )
