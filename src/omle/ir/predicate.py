"""Predicate IR classes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from ._util import enum_from_dict, obj_to_dict
from .enums import BooleanOperator, SimplePredicateOperator, SimpleSetOperator
from .types import Scalar


@dataclass
class TruePredicate:
    """Always-true predicate."""

    def to_dict(self) -> dict:
        return {}

    @classmethod
    def from_dict(cls, d: dict) -> "TruePredicate":
        return cls()


@dataclass
class FalsePredicate:
    """Always-false predicate."""

    def to_dict(self) -> dict:
        return {}

    @classmethod
    def from_dict(cls, d: dict) -> "FalsePredicate":
        return cls()


@dataclass
class SimplePredicate:
    """Simple comparison predicate on one column."""

    column: str = ""
    op: SimplePredicateOperator = SimplePredicateOperator.OPERATOR_UNSPECIFIED
    value: Optional[Scalar] = None

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "SimplePredicate":
        col_raw = d.get("column", "")
        if isinstance(col_raw, dict):
            col_raw = col_raw.get("name", "")
        return cls(
            column=col_raw,
            op=enum_from_dict(SimplePredicateOperator, d.get("op")),
            value=Scalar.from_dict(d["value"]) if "value" in d else None,
        )


@dataclass
class SimpleSetPredicate:
    """Set-membership predicate on one column."""

    column: str = ""
    op: SimpleSetOperator = SimpleSetOperator.OPERATOR_UNSPECIFIED
    values: list[Scalar] = field(default_factory=list)

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "SimpleSetPredicate":
        col_raw = d.get("column", "")
        if isinstance(col_raw, dict):
            col_raw = col_raw.get("name", "")
        return cls(
            column=col_raw,
            op=enum_from_dict(SimpleSetOperator, d.get("op")),
            values=[Scalar.from_dict(v) for v in d.get("values", [])],
        )


@dataclass
class CompoundPredicate:
    """Compound boolean predicate."""

    op: BooleanOperator = BooleanOperator.BOOLEAN_OPERATOR_UNSPECIFIED
    predicates: list["Predicate"] = field(default_factory=list)

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "CompoundPredicate":
        return cls(
            op=enum_from_dict(BooleanOperator, d.get("op")),
            predicates=[Predicate.from_dict(p) for p in d.get("predicates", [])],
        )


@dataclass
class Predicate:
    """Boolean predicate tree (oneof: true/false/simple/simple_set/compound)."""

    true_predicate: Optional[TruePredicate] = None
    false_predicate: Optional[FalsePredicate] = None
    simple: Optional[SimplePredicate] = None
    simple_set: Optional[SimpleSetPredicate] = None
    compound: Optional[CompoundPredicate] = None

    def __post_init__(self) -> None:
        set_fields = sum(
            1
            for v in (self.true_predicate, self.false_predicate, self.simple,
                      self.simple_set, self.compound)
            if v is not None
        )
        if set_fields > 1:
            raise ValueError("Predicate: only one branch may be set")

    # ── convenience constructors ──────────────────────────────────────────────

    @classmethod
    def true(cls) -> "Predicate":
        return cls(true_predicate=TruePredicate())

    @classmethod
    def false(cls) -> "Predicate":
        return cls(false_predicate=FalsePredicate())

    @classmethod
    def compare(cls, column: str, op: SimplePredicateOperator,
                value: Optional[Scalar] = None) -> "Predicate":
        return cls(simple=SimplePredicate(column=column, op=op, value=value))

    @classmethod
    def in_set(cls, column: str, values: list[Scalar]) -> "Predicate":
        return cls(simple_set=SimpleSetPredicate(
            column=column, op=SimpleSetOperator.IN, values=values,
        ))

    @classmethod
    def and_(cls, *predicates: "Predicate") -> "Predicate":
        return cls(compound=CompoundPredicate(op=BooleanOperator.AND, predicates=list(predicates)))

    @classmethod
    def or_(cls, *predicates: "Predicate") -> "Predicate":
        return cls(compound=CompoundPredicate(op=BooleanOperator.OR, predicates=list(predicates)))

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Predicate":
        return cls(
            true_predicate=TruePredicate.from_dict(d["true_predicate"])
                if "true_predicate" in d else None,
            false_predicate=FalsePredicate.from_dict(d["false_predicate"])
                if "false_predicate" in d else None,
            simple=SimplePredicate.from_dict(d["simple"]) if "simple" in d else None,
            simple_set=SimpleSetPredicate.from_dict(d["simple_set"])
                if "simple_set" in d else None,
            compound=CompoundPredicate.from_dict(d["compound"]) if "compound" in d else None,
        )
