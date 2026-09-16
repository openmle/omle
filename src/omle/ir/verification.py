"""ModelVerification, RuntimeWarmup, SampleInputSet, and related IR classes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from ._util import obj_to_dict
from .types import Scalar, TensorRef


@dataclass
class NumericTolerance:
    """Numeric comparison tolerance for verification."""

    atol: Optional[Scalar] = None
    rtol: Optional[Scalar] = None

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "NumericTolerance":
        return cls(
            atol=Scalar.from_dict(d["atol"]) if "atol" in d else None,
            rtol=Scalar.from_dict(d["rtol"]) if "rtol" in d else None,
        )


@dataclass
class VerificationCase:
    """One verification case with expected inputs and outputs."""

    inputs: list[TensorRef] = field(default_factory=list)
    expected_outputs: list[TensorRef] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "VerificationCase":
        return cls(
            inputs=[TensorRef.from_dict(r) for r in d.get("inputs", [])],
            expected_outputs=[TensorRef.from_dict(r) for r in d.get("expected_outputs", [])],
            description=d.get("description", ""),
        )


@dataclass
class ModelVerification:
    """Verification cases for model correctness."""

    cases: list[VerificationCase] = field(default_factory=list)
    tolerance: Optional[NumericTolerance] = None

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "ModelVerification":
        return cls(
            cases=[VerificationCase.from_dict(c) for c in d.get("cases", [])],
            tolerance=NumericTolerance.from_dict(d["tolerance"]) if "tolerance" in d else None,
        )


@dataclass
class WarmupCase:
    """One warm-up execution case."""

    inputs: list[TensorRef] = field(default_factory=list)
    description: str = ""
    repeat: int = 0

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "WarmupCase":
        return cls(
            inputs=[TensorRef.from_dict(r) for r in d.get("inputs", [])],
            description=d.get("description", ""),
            repeat=d.get("repeat", 0),
        )


@dataclass
class RuntimeWarmup:
    """Warm-up requests for runtime initialization."""

    cases: list[WarmupCase] = field(default_factory=list)

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "RuntimeWarmup":
        return cls(cases=[WarmupCase.from_dict(c) for c in d.get("cases", [])])


@dataclass
class SampleInputCase:
    """One sample input case."""

    inputs: list[TensorRef] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "SampleInputCase":
        return cls(
            inputs=[TensorRef.from_dict(r) for r in d.get("inputs", [])],
            description=d.get("description", ""),
        )


@dataclass
class SampleInputSet:
    """Sample inputs for end-user reference."""

    cases: list[SampleInputCase] = field(default_factory=list)

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "SampleInputSet":
        return cls(cases=[SampleInputCase.from_dict(c) for c in d.get("cases", [])])
