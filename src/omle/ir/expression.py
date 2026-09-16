"""Expression and Apply IR classes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from ._util import obj_to_dict
from .types import Scalar


@dataclass
class Apply:
    """Elementwise primitive application."""

    function: str = ""
    arguments: list["Expression"] = field(default_factory=list)

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Apply":
        return cls(
            function=d.get("function", ""),
            arguments=[Expression.from_dict(a) for a in d.get("arguments", [])],
        )


@dataclass
class Expression:
    """Tensor expression over row-aligned named values (oneof: literal/ref/apply)."""

    literal: Optional[Scalar] = None
    ref: Optional[str] = None
    apply: Optional[Apply] = None

    def __post_init__(self) -> None:
        set_fields = sum(1 for v in (self.literal, self.ref, self.apply) if v is not None)
        if set_fields > 1:
            raise ValueError("Expression: only one of literal, ref, or apply may be set")

    # ── convenience constructors ──────────────────────────────────────────────

    @classmethod
    def from_literal(cls, scalar: Scalar) -> "Expression":
        return cls(literal=scalar)

    @classmethod
    def from_ref(cls, name: str) -> "Expression":
        return cls(ref=name)

    @classmethod
    def from_apply(cls, function: str, *args: "Expression") -> "Expression":
        return cls(apply=Apply(function=function, arguments=list(args)))

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Expression":
        ref_raw = d.get("ref", d.get("column"))  # accept old "column" key for compat
        if isinstance(ref_raw, dict):
            ref_raw = ref_raw.get("value", ref_raw.get("name", ""))
        return cls(
            literal=Scalar.from_dict(d["literal"]) if "literal" in d else None,
            ref=ref_raw,
            apply=Apply.from_dict(d["apply"]) if "apply" in d else None,
        )
