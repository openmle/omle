"""OMLEModel root IR class."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from ._util import obj_to_dict
from .function import DefineFunction
from .interface import InputSpec, OutputSpec
from .metadata import ModelMetadata, NamespaceImport
from .node import Node
from .schema import ModelSchema
from .tensor import TensorEntry
from .verification import ModelVerification, RuntimeWarmup, SampleInputSet


@dataclass
class OMLEModel:
    """Root OMLE model document."""

    metadata: ModelMetadata = field(default_factory=ModelMetadata)
    operator_imports: list[NamespaceImport] = field(default_factory=list)
    function_imports: list[NamespaceImport] = field(default_factory=list)
    inputs: list[InputSpec] = field(default_factory=list)
    outputs: list[OutputSpec] = field(default_factory=list)
    model_schema: Optional[ModelSchema] = None
    nodes: list[Node] = field(default_factory=list)
    verification: Optional[ModelVerification] = None
    warmup: Optional[RuntimeWarmup] = None
    sample_inputs: Optional[SampleInputSet] = None
    tensor_entries: list[TensorEntry] = field(default_factory=list)
    functions: list[DefineFunction] = field(default_factory=list)

    # ── dict / JSON ───────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "OMLEModel":
        return cls(
            metadata=ModelMetadata.from_dict(d["metadata"]) if "metadata" in d
                else ModelMetadata(),
            operator_imports=[NamespaceImport.from_dict(i)
                              for i in d.get("operator_imports", [])],
            function_imports=[NamespaceImport.from_dict(i)
                              for i in d.get("function_imports", [])],
            inputs=[InputSpec.from_dict(i) for i in d.get("inputs", [])],
            outputs=[OutputSpec.from_dict(o) for o in d.get("outputs", [])],
            model_schema=ModelSchema.from_dict(d["model_schema"])
                if "model_schema" in d else None,
            nodes=[Node.from_dict(n) for n in d.get("nodes", [])],
            tensor_entries=[TensorEntry.from_dict(c) for c in d.get("tensor_entries", [])],
            functions=[DefineFunction.from_dict(f) for f in d.get("functions", [])],
            verification=ModelVerification.from_dict(d["verification"])
                if "verification" in d else None,
            warmup=RuntimeWarmup.from_dict(d["warmup"]) if "warmup" in d else None,
            sample_inputs=SampleInputSet.from_dict(d["sample_inputs"])
                if "sample_inputs" in d else None,
        )

    # ── convenience accessors ─────────────────────────────────────────────────

    def get_tensor_entry(self, id: str) -> Optional[TensorEntry]:
        """Look up a tensor entry by its id."""
        for e in self.tensor_entries:
            if e.id == id:
                return e
        return None

    def get_node(self, name: str) -> Optional[Node]:
        """Look up a node by name."""
        for n in self.nodes:
            if n.name == name:
                return n
        return None

    def input_names(self) -> list[str]:
        return [i.name for i in self.inputs]

    def output_names(self) -> list[str]:
        return [o.name for o in self.outputs]

    def node_output_names(self) -> list[str]:
        """All NodeOutput names visible in the top-level graph namespace."""
        names: list[str] = []
        for node in self.nodes:
            for out in node.outputs:
                names.append(out.name)
        return names

    def _repr_html_(self) -> str:
        try:
            from omle_viewer.display import model_repr_html
            return model_repr_html(self)
        except ImportError:
            import json as _json
            data = _json.dumps(self.to_dict(), indent=2)
            banner = (
                '<div style="padding:8px 12px;margin-bottom:6px;font-family:sans-serif;'
                'font-size:12px;color:#856404;background:#fff3cd;border:1px solid #ffc107;'
                'border-radius:4px">'
                '<strong>omle-viewer not installed.</strong> '
                'Install it to render the interactive diagram: '
                '<code>pip install omle-viewer</code>'
                '</div>'
            )
            return f'{banner}<pre style="font-size:12px;overflow:auto;max-height:400px">{data}</pre>'
