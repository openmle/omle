"""OMLEModel root IR class."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional

from ._util import obj_to_dict
from .function import DefineFunction
from .interface import InputSpec, OutputSpec
from .metadata import ModelMetadata, NamespaceImport
from .node import Node
from .schema import ModelSchema
from .tensor import TensorEntry
from .verification import ModelVerification, RuntimeWarmup, SampleInputSet

if TYPE_CHECKING:  # pragma: no cover - typing only
    import omle_runtime


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

    # ── Runtime interop ───────────────────────────────────────────────────────

    def to_runtime(
        self,
        *,
        n_threads: int = 1,
        min_parallel_rows: int = 64,
    ) -> "omle_runtime.Model":
        """Build a new :class:`omle_runtime.Model` from this document.

        Always builds; nothing is cached or reused, so the handle reflects the
        document exactly as it stands right now. That costs one protobuf
        serialization plus a native load — roughly 1.5 ms for a small model and
        160 ms for one carrying a couple of thousand tensors.

        Hold on to the result to score repeatedly. The returned model is
        immutable and thread-safe, and it does not track later edits to this
        document; call this again to pick those up.

        Requires the optional runtime: ``pip install omle-runtime``.
        """
        try:
            import omle_runtime
        except ImportError as exc:  # pragma: no cover - depends on the env
            raise ImportError(
                "omle_runtime is required to score a model.\n"
                "Install it with:  pip install omle-runtime"
            ) from exc

        from ..io import to_proto_bytes

        return omle_runtime.Model.load_bytes(
            to_proto_bytes(self),
            n_threads=n_threads,
            min_parallel_rows=min_parallel_rows,
        )

    def _runtime_for_predict(self) -> "omle_runtime.Model":
        """The handle backing :meth:`predict` — built once, then reused.

        Only the prediction shortcuts share this. :meth:`to_runtime` always
        builds fresh, so a caller who wants a handle tracking the current
        document gets one without having to know about this cache.
        """
        runtime = getattr(self, "_runtime", None)
        if runtime is None:
            runtime = self.to_runtime()
            self._runtime = runtime
        return runtime

    def invalidate_runtime(self) -> None:
        """Drop the handle cached for :meth:`predict` / :meth:`predict_proba`.

        Call this after editing the document. A nested edit such as
        ``model.nodes[0].tree.values[3] = 0.5`` never reaches this object, so
        staleness cannot be detected here — declaring it is the caller's job.
        """
        self._runtime = None

    # noqa N803: X is scikit-learn's parameter name for the feature matrix.
    # Renaming it would break the convention these methods exist to follow,
    # and callers who pass X= by keyword.
    def predict(self, X: Any) -> Any:  # noqa: N803
        """Batch prediction, with scikit-learn's calling convention.

        Builds a runtime model on first use and reuses it, so edits made
        afterwards need :meth:`invalidate_runtime`. For explicit control over
        that lifetime, use :meth:`to_runtime` and call it directly.
        """
        return self._runtime_for_predict().predict(X)

    # noqa N803: see predict above.
    def predict_proba(self, X: Any) -> Any:  # noqa: N803
        """Per-class probabilities, with scikit-learn's calling convention.

        Shares the cached handle — and the caveat — described on :meth:`predict`.
        """
        return self._runtime_for_predict().predict_proba(X)

    # ── pickling ──────────────────────────────────────────────────────────────

    def __getstate__(self) -> dict:
        """Leave the cached runtime handle out of pickles and copies.

        ``omle_runtime.Model`` pickles by carrying its serialized bytes, so
        keeping it would roughly double the payload and make ``copy.deepcopy``
        silently rebuild a native model.
        """
        return {k: v for k, v in vars(self).items() if not k.startswith("_")}

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
