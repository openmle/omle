"""ModelMetadata, SourceFramework, and NamespaceImport IR classes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from ._util import obj_to_dict


@dataclass
class SourceFramework:
    """One framework or library involved in the original source pipeline."""

    name: str = ""
    version: str = ""
    role: str = ""

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "SourceFramework":
        return cls(
            name=d.get("name", ""),
            version=d.get("version", ""),
            role=d.get("role", ""),
        )


@dataclass
class ModelMetadata:
    """Descriptive metadata for the model artifact."""

    format_version: str = "0.1.0"
    name: str = ""
    version: str = ""
    timestamp: str = ""
    producer: str = ""
    producer_version: str = ""
    source_frameworks: List[SourceFramework] = field(default_factory=list)
    doc_string: str = ""
    copyright: str = ""
    attributes: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "ModelMetadata":
        return cls(
            format_version=d.get("format_version", "0.1.0"),
            name=d.get("name", ""),
            version=d.get("version", ""),
            timestamp=d.get("timestamp", ""),
            producer=d.get("producer", ""),
            producer_version=d.get("producer_version", ""),
            source_frameworks=[
                SourceFramework.from_dict(f)
                for f in d.get("source_frameworks", [])
            ],
            doc_string=d.get("doc_string", ""),
            copyright=d.get("copyright", ""),
            attributes=dict(d.get("attributes", {})),
        )


@dataclass
class NamespaceImport:
    """Imported operator or function namespace and version."""

    namespace: str = ""
    version: str = ""

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "NamespaceImport":
        return cls(namespace=d.get("namespace", ""), version=d.get("version", ""))
