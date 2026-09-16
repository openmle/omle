"""ModelSchema, Feature, Target, NameRange IR classes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from ._util import enum_from_dict, obj_to_dict
from .domain import ValueDomain
from .enums import (
    InvalidValuePolicy,
    MeasureLevel,
    MissingValuePolicy,
    OutlierValuePolicy,
    TargetKind,
)
from .types import Scalar, TensorType


@dataclass
class NameRange:
    """Auto-generated range of feature/input names: prefix + str(i) for i in [start, end)."""

    prefix: str = ""
    start: int = 0
    end: int = 0
    width: int = 0

    def expand(self) -> list[str]:
        """Return the list of expanded names."""
        fmt = f"{{:0{self.width}d}}" if self.width > 0 else "{}"
        return [f"{self.prefix}{fmt.format(i)}" for i in range(self.start, self.end)]

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "NameRange":
        return cls(
            prefix=d.get("prefix", ""),
            start=d.get("start", 0),
            end=d.get("end", 0),
            width=d.get("width", 0),
        )


@dataclass
class Feature:
    """Logical feature description."""

    # oneof naming
    name: Optional[str] = None
    range: Optional[NameRange] = None

    description: str = ""
    type: Optional[TensorType] = None
    measure_level: MeasureLevel = MeasureLevel.MEASURE_LEVEL_UNSPECIFIED
    source: str = ""
    index: int = 0
    missing_value_policy: MissingValuePolicy = MissingValuePolicy.MISSING_PROPAGATE
    missing_replacement_value: Optional[Scalar] = None
    invalid_value_policy: InvalidValuePolicy = InvalidValuePolicy.INVALID_RETURN_INVALID
    invalid_replacement_value: Optional[Scalar] = None
    outlier_value_policy: OutlierValuePolicy = OutlierValuePolicy.OUTLIER_AS_IS
    domain: Optional[ValueDomain] = None
    attributes: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.name is not None and self.range is not None:
            raise ValueError("Feature: only one of name or range may be set")

    def expand_names(self) -> list[str]:
        """Return the list of logical feature names this declaration covers."""
        if self.name is not None:
            return [self.name]
        if self.range is not None:
            return self.range.expand()
        return []

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Feature":
        return cls(
            name=d.get("name"),
            range=NameRange.from_dict(d["range"]) if "range" in d else None,
            description=d.get("description", ""),
            type=TensorType.from_dict(d["type"]) if "type" in d else None,
            measure_level=enum_from_dict(MeasureLevel, d.get("measure_level")),
            source=d.get("source", ""),
            index=d.get("index", 0),
            missing_value_policy=enum_from_dict(MissingValuePolicy, d.get("missing_value_policy")),
            missing_replacement_value=(
                Scalar.from_dict(d["missing_replacement_value"])
                if "missing_replacement_value" in d else None
            ),
            invalid_value_policy=enum_from_dict(InvalidValuePolicy, d.get("invalid_value_policy")),
            invalid_replacement_value=(
                Scalar.from_dict(d["invalid_replacement_value"])
                if "invalid_replacement_value" in d else None
            ),
            outlier_value_policy=enum_from_dict(OutlierValuePolicy, d.get("outlier_value_policy")),
            domain=ValueDomain.from_dict(d["domain"]) if "domain" in d else None,
            attributes=dict(d.get("attributes", {})),
        )


@dataclass
class Target:
    """Logical target field description."""

    name: str = ""
    type: Optional[TensorType] = None
    kind: TargetKind = TargetKind.TARGET_KIND_UNSPECIFIED
    measure_level: MeasureLevel = MeasureLevel.MEASURE_LEVEL_UNSPECIFIED
    class_labels: list[Scalar] = field(default_factory=list)
    description: str = ""
    attributes: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Target":
        return cls(
            name=d.get("name", ""),
            type=TensorType.from_dict(d["type"]) if "type" in d else None,
            kind=enum_from_dict(TargetKind, d.get("kind")),
            measure_level=enum_from_dict(MeasureLevel, d.get("measure_level")),
            class_labels=[Scalar.from_dict(s) for s in d.get("class_labels", [])],
            description=d.get("description", ""),
            attributes=dict(d.get("attributes", {})),
        )


@dataclass
class ModelSchema:
    """Logical feature/target schema acting as an initial preprocessing stage."""

    features: list[Feature] = field(default_factory=list)
    targets: list[Target] = field(default_factory=list)

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "ModelSchema":
        return cls(
            features=[Feature.from_dict(f) for f in d.get("features", [])],
            targets=[Target.from_dict(t) for t in d.get("targets", [])],
        )
