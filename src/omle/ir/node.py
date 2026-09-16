"""Node, NodeInput, NodeOutput, NameAlias, CompositeNode, Attribute IR classes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# Import body types lazily to avoid circular issues
from . import bodies as _bodies
from ._util import enum_from_dict, ints_from_dict, obj_to_dict
from .domain import ValueDomain
from .enums import MeasureLevel, OutputRole
from .expression import Expression
from .interface import OutputBinding
from .predicate import Predicate
from .schema import NameRange
from .tensor import SparseTensor, Tensor
from .types import NameRef, TensorRef, TensorType


@dataclass
class NodeInput:
    """One input reference consumed by a Node (oneof: name/range)."""

    name: Optional[NameRef] = None
    range: Optional[NameRange] = None

    def __post_init__(self) -> None:
        if isinstance(self.name, str):
            self.name = NameRef(value=self.name)
        if self.name is not None and self.range is not None:
            raise ValueError("NodeInput: only one of name or range may be set")

    def to_dict(self) -> dict:
        d: dict = {}
        if self.name is not None:
            d["name"] = self.name.to_dict()
        if self.range is not None:
            d["range"] = self.range.to_dict()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "NodeInput":
        name_raw = d.get("name")
        return cls(
            name=NameRef.from_dict(name_raw) if name_raw is not None else None,
            range=NameRange.from_dict(d["range"]) if "range" in d else None,
        )


@dataclass
class NodeOutput:
    """One output value produced by a Node."""

    name: str = ""
    type: Optional[TensorType] = None
    measure_level: MeasureLevel = MeasureLevel.MEASURE_LEVEL_UNSPECIFIED
    domain: Optional[ValueDomain] = None
    description: str = ""
    role: OutputRole = OutputRole.OUTPUT_ROLE_UNSPECIFIED
    binding: Optional[OutputBinding] = None
    field_names: list[str] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "NodeOutput":
        return cls(
            name=d.get("name", ""),
            type=TensorType.from_dict(d["type"]) if "type" in d else None,
            measure_level=enum_from_dict(MeasureLevel, d.get("measure_level")),
            domain=ValueDomain.from_dict(d["domain"]) if "domain" in d else None,
            description=d.get("description", ""),
            role=enum_from_dict(OutputRole, d.get("role")),
            binding=OutputBinding.from_dict(d["binding"]) if "binding" in d else None,
            field_names=list(d.get("field_names", [])),
            attributes=dict(d.get("attributes", {})),
        )


@dataclass
class NameAlias:
    """Renames one name to another at a scope boundary."""

    from_name: str = ""
    to_name: str = ""

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "NameAlias":
        return cls(from_name=d.get("from_name", ""), to_name=d.get("to_name", ""))


@dataclass
class CompositeNode:
    """Composite node body: a subgraph executed in a local namespace."""

    input_aliases: list[NameAlias] = field(default_factory=list)
    nodes: list["Node"] = field(default_factory=list)
    output_aliases: list[NameAlias] = field(default_factory=list)

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "CompositeNode":
        return cls(
            input_aliases=[NameAlias.from_dict(a) for a in d.get("input_aliases", [])],
            nodes=[Node.from_dict(n) for n in d.get("nodes", [])],
            output_aliases=[NameAlias.from_dict(a) for a in d.get("output_aliases", [])],
        )


@dataclass
class Attribute:
    """Generic attribute attached to a node (oneof value)."""

    name: str = ""
    # oneof value
    i: Optional[int] = None
    f32: Optional[float] = None
    f64: Optional[float] = None
    s: Optional[str] = None
    b: Optional[bool] = None
    ints: Optional[list[int]] = None
    float32s: Optional[list[float]] = None
    float64s: Optional[list[float]] = None
    strings: Optional[list[str]] = None
    bools: Optional[list[bool]] = None
    tensor_ref: Optional[TensorRef] = None
    tensor: Optional[Tensor] = None
    sparse: Optional[SparseTensor] = None
    type: Optional[TensorType] = None
    expr: Optional[Expression] = None
    predicate: Optional[Predicate] = None

    def to_dict(self) -> dict:
        d: dict = {"name": self.name}
        for key in ("i", "f32", "f64", "s", "b", "ints", "float32s", "float64s",
                    "strings", "bools"):
            val = getattr(self, key)
            if val is not None:
                d[key] = val
        if self.tensor_ref is not None:
            d["tensor_ref"] = self.tensor_ref.to_dict()
        if self.tensor is not None:
            d["tensor"] = self.tensor.to_dict()
        if self.sparse is not None:
            d["sparse"] = self.sparse.to_dict()
        if self.type is not None:
            d["type"] = self.type.to_dict()
        if self.expr is not None:
            d["expr"] = self.expr.to_dict()
        if self.predicate is not None:
            d["predicate"] = self.predicate.to_dict()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Attribute":
        return cls(
            name=d.get("name", ""),
            i=d.get("i"),
            f32=d.get("f32"),
            f64=d.get("f64"),
            s=d.get("s"),
            b=d.get("b"),
            ints=ints_from_dict(d["ints"]) if "ints" in d else None,
            float32s=list(d["float32s"]) if "float32s" in d else None,
            float64s=list(d["float64s"]) if "float64s" in d else None,
            strings=list(d["strings"]) if "strings" in d else None,
            bools=list(d["bools"]) if "bools" in d else None,
            tensor_ref=TensorRef.from_dict(d["tensor_ref"]) if "tensor_ref" in d else None,
            tensor=Tensor.from_dict(d["tensor"]) if "tensor" in d else None,
            sparse=SparseTensor.from_dict(d["sparse"]) if "sparse" in d else None,
            type=TensorType.from_dict(d["type"]) if "type" in d else None,
            expr=Expression.from_dict(d["expr"]) if "expr" in d else None,
            predicate=Predicate.from_dict(d["predicate"]) if "predicate" in d else None,
        )


@dataclass
class Node:
    """Graph node representing a computation stage."""

    name: str = ""
    domain: str = ""
    op: str = ""
    inputs: list[NodeInput] = field(default_factory=list)
    outputs: list[NodeOutput] = field(default_factory=list)
    attributes: list[Attribute] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)

    # body oneof
    composite: Optional[CompositeNode] = None
    tree: Optional[_bodies.Tree] = None
    tree_ensemble: Optional[_bodies.TreeEnsemble] = None
    linear: Optional[_bodies.Linear] = None
    naive_bayes: Optional[_bodies.NaiveBayes] = None
    clustering: Optional[_bodies.Clustering] = None
    svm: Optional[_bodies.SVM] = None
    neural_network: Optional[_bodies.NeuralNetwork] = None
    anomaly_detection: Optional[_bodies.AnomalyDetection] = None

    _BODY_KEYS = (
        "composite", "tree", "tree_ensemble",
        "linear", "naive_bayes", "clustering", "svm", "neural_network",
        "anomaly_detection",
    )

    def body(self):
        """Return the active body object or None."""
        for key in self._BODY_KEYS:
            v = getattr(self, key)
            if v is not None:
                return v
        return None

    def to_dict(self) -> dict:
        d: dict = {}
        if self.name:
            d["name"] = self.name
        if self.domain:
            d["domain"] = self.domain
        if self.op:
            d["op"] = self.op
        if self.inputs:
            d["inputs"] = [i.to_dict() for i in self.inputs]
        if self.outputs:
            d["outputs"] = [o.to_dict() for o in self.outputs]
        if self.attributes:
            d["attributes"] = [a.to_dict() for a in self.attributes]
        if self.metadata:
            d["metadata"] = dict(self.metadata)
        for key in self._BODY_KEYS:
            v = getattr(self, key)
            if v is not None:
                d[key] = v.to_dict()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Node":
        return cls(
            name=d.get("name", ""),
            domain=d.get("domain", ""),
            op=d.get("op", ""),
            inputs=[NodeInput.from_dict(i) for i in d.get("inputs", [])],
            outputs=[NodeOutput.from_dict(o) for o in d.get("outputs", [])],
            attributes=[Attribute.from_dict(a) for a in d.get("attributes", [])],
            metadata=dict(d.get("metadata", {})),
            composite=CompositeNode.from_dict(d["composite"]) if "composite" in d else None,
            tree=_bodies.Tree.from_dict(d["tree"]) if "tree" in d else None,
            tree_ensemble=_bodies.TreeEnsemble.from_dict(d["tree_ensemble"])
                if "tree_ensemble" in d else None,
            linear=_bodies.Linear.from_dict(d["linear"]) if "linear" in d else None,
            naive_bayes=_bodies.NaiveBayes.from_dict(d["naive_bayes"])
                if "naive_bayes" in d else None,
            clustering=_bodies.Clustering.from_dict(d["clustering"])
                if "clustering" in d else None,
            svm=_bodies.SVM.from_dict(d["svm"]) if "svm" in d else None,
            neural_network=_bodies.NeuralNetwork.from_dict(d["neural_network"])
                if "neural_network" in d else None,
            anomaly_detection=_bodies.AnomalyDetection.from_dict(d["anomaly_detection"])
                if "anomaly_detection" in d else None,
        )
