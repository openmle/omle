"""DefineFunction IR class."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from ._util import enum_from_dict, obj_to_dict
from .enums import DataType, MeasureLevel
from .expression import Expression


@dataclass
class FunctionParameter:
    """One parameter of a user-defined function."""

    name: str = ""
    data_type: DataType = DataType.DATA_TYPE_UNSPECIFIED
    measure_level: MeasureLevel = MeasureLevel.MEASURE_LEVEL_UNSPECIFIED

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "FunctionParameter":
        return cls(
            name=d.get("name", ""),
            data_type=enum_from_dict(DataType, d.get("data_type")),
            measure_level=enum_from_dict(MeasureLevel, d.get("measure_level")),
        )


@dataclass
class DefineFunction:
    """User-defined elementwise function declaration."""

    name: str = ""
    doc_string: str = ""
    parameters: list[FunctionParameter] = field(default_factory=list)
    result_data_type: DataType = DataType.DATA_TYPE_UNSPECIFIED
    result_measure_level: MeasureLevel = MeasureLevel.MEASURE_LEVEL_UNSPECIFIED
    body: Optional[Expression] = None
    attributes: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "DefineFunction":
        return cls(
            name=d.get("name", ""),
            doc_string=d.get("doc_string", ""),
            parameters=[FunctionParameter.from_dict(p) for p in d.get("parameters", [])],
            result_data_type=enum_from_dict(DataType, d.get("result_data_type")),
            result_measure_level=enum_from_dict(MeasureLevel, d.get("result_measure_level")),
            body=Expression.from_dict(d["body"]) if "body" in d else None,
            attributes=dict(d.get("attributes", {})),
        )
