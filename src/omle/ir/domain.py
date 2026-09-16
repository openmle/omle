"""ValueDomain, ContinuousDomain, DiscreteDomain, Interval, DomainValue IR classes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from ._util import enum_from_dict, obj_to_dict
from .enums import IntervalClosure, ValueProperty
from .types import Scalar


@dataclass
class Interval:
    """Numeric interval declaration."""

    left_margin: Optional[Scalar] = None
    right_margin: Optional[Scalar] = None
    closure: IntervalClosure = IntervalClosure.CLOSURE_UNSPECIFIED

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Interval":
        return cls(
            left_margin=Scalar.from_dict(d["left_margin"]) if "left_margin" in d else None,
            right_margin=Scalar.from_dict(d["right_margin"]) if "right_margin" in d else None,
            closure=enum_from_dict(IntervalClosure, d.get("closure")),
        )


@dataclass
class ContinuousDomain:
    """Continuous numeric domain defined by intervals."""

    intervals: list[Interval] = field(default_factory=list)

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "ContinuousDomain":
        return cls(intervals=[Interval.from_dict(i) for i in d.get("intervals", [])])


@dataclass
class DomainValue:
    """One declared value inside a discrete domain."""

    value: Optional[Scalar] = None
    original_value: Optional[Scalar] = None
    display_name: str = ""
    property: ValueProperty = ValueProperty.VALID

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "DomainValue":
        return cls(
            value=Scalar.from_dict(d["value"]) if "value" in d else None,
            original_value=Scalar.from_dict(d["original_value"]) if "original_value" in d else None,
            display_name=d.get("display_name", ""),
            property=enum_from_dict(ValueProperty, d.get("property")),
        )


@dataclass
class DiscreteDomain:
    """Discrete or categorical domain."""

    values: list[DomainValue] = field(default_factory=list)
    ordered: bool = False

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "DiscreteDomain":
        return cls(
            values=[DomainValue.from_dict(v) for v in d.get("values", [])],
            ordered=d.get("ordered", False),
        )


@dataclass
class ValueDomain:
    """Declared value domain for a feature or output (oneof: continuous/discrete)."""

    continuous: Optional[ContinuousDomain] = None
    discrete: Optional[DiscreteDomain] = None

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "ValueDomain":
        return cls(
            continuous=ContinuousDomain.from_dict(d["continuous"]) if "continuous" in d else None,
            discrete=DiscreteDomain.from_dict(d["discrete"]) if "discrete" in d else None,
        )
