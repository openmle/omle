"""Tests for IR ↔ protobuf conversion (omle.proto.convert)."""

from __future__ import annotations

import pytest

from omle import (
    Apply,
    DataType,
    DefineFunction,
    Expression,
    Feature,
    FunctionParameter,
    InputSpec,
    Linear,
    MeasureLevel,
    ModelMetadata,
    ModelSchema,
    NamespaceImport,
    Node,
    NodeInput,
    NodeOutput,
    OMLEModel,
    OutputRole,
    OutputSpec,
    PostTransform,
    Scalar,
    SourceFramework,
    Target,
    TargetKind,
    Tensor,
    TensorEntry,
    TensorRef,
    TensorType,
    TensorValue,
    Tree,
    TreeAggregation,
    TreeEnsemble,
    TreeNodeKind,
    TreeSplitOp,
)

pb2 = pytest.importorskip(
    "omle.proto.omle_pb2",
    reason="omle_pb2 not generated; run scripts/gen_proto.sh",
)

from omle.proto.convert import (  # noqa: E402
    ir_to_bytes,
    ir_to_proto,
    proto_to_ir,
)

# ── helpers ───────────────────────────────────────────────────────────────────

def _proto_to_json_str(msg) -> str:
    from google.protobuf import json_format
    return json_format.MessageToJson(
        msg,
        preserving_proto_field_name=True,
        indent=2,
    )


def _print_proto_json(msg, label: str, enabled: bool) -> None:
    if not enabled:
        return
    print(f"\n{'─' * 60}")
    print(f"  {label}")
    print('─' * 60)
    print(_proto_to_json_str(msg))


def _build_linear_model() -> OMLEModel:
    return OMLEModel(
        metadata=ModelMetadata(
            format_version="0.1.0",
            name="linear_iris",
            producer="test",
            source_frameworks=[SourceFramework(name="scikit-learn")],
        ),
        operator_imports=[NamespaceImport(namespace="omle.ml", version="0.1")],
        inputs=[InputSpec(name="X", type=TensorType(dtype=DataType.FLOAT32, shape=[-1, 4]))],
        outputs=[OutputSpec(name="y_pred", role=OutputRole.PREDICTION)],
        model_schema=ModelSchema(
            features=[
                Feature(name="sl", source="X", index=0,
                        type=TensorType(dtype=DataType.FLOAT32, shape=[-1]),
                        measure_level=MeasureLevel.CONTINUOUS),
            ],
            targets=[
                Target(name="species", kind=TargetKind.MULTICLASS,
                       class_labels=[Scalar.string(s) for s in
                                     ("setosa", "versicolor", "virginica")])
            ],
        ),
        tensor_entries=[
            TensorEntry(id="coef", dense=Tensor(
                name="coef",
                type=TensorType(dtype=DataType.FLOAT32, shape=[3, 4]),
                float32_data=[0.1] * 12,
            )),
            TensorEntry(id="bias", dense=Tensor(
                name="bias",
                type=TensorType(dtype=DataType.FLOAT32, shape=[3]),
                float32_data=[0.0, 0.0, 0.0],
            )),
        ],
        nodes=[
            Node(
                name="clf",
                domain="omle.ml",
                op="LinearClassifier",
                inputs=[NodeInput(name="X")],
                outputs=[NodeOutput(name="y_pred", role=OutputRole.PREDICTION)],
                linear=Linear(
                    coefficients=TensorValue.of_ref(TensorRef(id="coef")),
                    intercept=TensorValue.of_tensor(Tensor(float64_data=[0.5])),
                    post_transform=PostTransform.SOFTMAX,
                ),
            )
        ],
    )


def _build_tree_ensemble_model() -> OMLEModel:
    tree = Tree(
        num_nodes=3,
        node_kind=[TreeNodeKind.BRANCH, TreeNodeKind.LEAF, TreeNodeKind.LEAF],
        split_feature=[0],
        split_threshold=TensorValue.of_tensor(Tensor(float64_data=[0.5])),
        split_op=[TreeSplitOp.LESS_THAN],
        children_index=[1, 2],
        children_offset=[0],
        children_count=[2],
        default_child=[1],
        leaf_value=TensorValue.of_tensor(Tensor(float64_data=[0.0, 1.0])),
    )
    return OMLEModel(
        metadata=ModelMetadata(
            format_version="0.1.0",
            name="tree_ensemble_model",
            producer="test",
        ),
        inputs=[InputSpec(name="X")],
        outputs=[OutputSpec(name="y_pred", role=OutputRole.PREDICTION)],
        nodes=[
            Node(
                name="ensemble",
                domain="omle.ml",
                op="TreeEnsembleClassifier",
                inputs=[NodeInput(name="X")],
                outputs=[NodeOutput(name="y_pred", role=OutputRole.PREDICTION)],
                tree_ensemble=TreeEnsemble(
                    trees=[tree],
                    aggregation=TreeAggregation.SUM,
                    post_transform=PostTransform.SIGMOID,
                    base_scores=TensorValue.of_tensor(Tensor(float64_data=[0.5])),
                ),
            )
        ],
    )


def _build_function_model() -> OMLEModel:
    return OMLEModel(
        metadata=ModelMetadata(
            format_version="0.1.0",
            name="function_model",
            producer="test",
        ),
        function_imports=[NamespaceImport(namespace="omle.functions", version="0.1")],
        inputs=[InputSpec(name="X")],
        outputs=[OutputSpec(name="y", role=OutputRole.PREDICTION)],
        nodes=[],
        functions=[
            DefineFunction(
                name="scale2x",
                parameters=[FunctionParameter(name="x", data_type=DataType.FLOAT64)],
                result_data_type=DataType.FLOAT64,
                body=Expression(apply=Apply(
                    function="mul",
                    arguments=[
                        Expression.from_ref("x"),
                        Expression.from_literal(Scalar.float(2.0)),
                    ],
                )),
            )
        ],
    )


# ── ir_to_proto ───────────────────────────────────────────────────────────────

def test_ir_to_proto_linear(proto_json):
    model = _build_linear_model()
    msg = ir_to_proto(model)
    _print_proto_json(msg, "Linear model proto JSON", proto_json)

    assert msg.metadata.name == "linear_iris"
    assert msg.metadata.format_version == "0.1.0"
    assert len(msg.inputs) == 1
    assert msg.inputs[0].name == "X"
    assert len(msg.outputs) == 1
    assert msg.outputs[0].name == "y_pred"
    assert len(msg.nodes) == 1
    node = msg.nodes[0]
    assert node.name == "clf"
    assert node.linear.coefficients.tensor_ref.id == "coef"
    assert list(node.linear.intercept.tensor.float64_data.values) == [0.5]
    assert len(msg.tensor_entries) == 2
    assert msg.tensor_entries[0].id == "coef"


def test_ir_to_proto_tree_ensemble(proto_json):
    model = _build_tree_ensemble_model()
    msg = ir_to_proto(model)
    _print_proto_json(msg, "TreeEnsemble model proto JSON", proto_json)

    assert msg.metadata.name == "tree_ensemble_model"
    node = msg.nodes[0]
    assert len(node.tree_ensemble.trees) == 1
    assert node.tree_ensemble.trees[0].num_nodes == 3
    assert node.tree_ensemble.aggregation == TreeAggregation.SUM.value
    assert abs(node.tree_ensemble.base_scores.tensor.float64_data.values[0] - 0.5) < 1e-9


def test_ir_to_proto_functions(proto_json):
    model = _build_function_model()
    msg = ir_to_proto(model)
    _print_proto_json(msg, "Function model proto JSON", proto_json)

    assert len(msg.function_imports) == 1
    assert msg.function_imports[0].namespace == "omle.functions"
    assert len(msg.functions) == 1
    fn = msg.functions[0]
    assert fn.name == "scale2x"
    assert len(fn.parameters) == 1
    assert fn.parameters[0].name == "x"


def test_ir_to_proto_model_schema(proto_json):
    model = _build_linear_model()
    msg = ir_to_proto(model)
    _print_proto_json(msg, "Model schema proto JSON", proto_json)

    schema = msg.model_schema
    assert len(schema.features) == 1
    assert schema.features[0].name == "sl"
    assert len(schema.targets) == 1
    assert schema.targets[0].name == "species"
    assert len(schema.targets[0].class_labels) == 3


# ── ir_to_bytes ───────────────────────────────────────────────────────────────

def test_ir_to_bytes_produces_bytes():
    model = _build_linear_model()
    raw = ir_to_bytes(model)
    assert isinstance(raw, bytes)
    assert len(raw) > 0


def test_ir_to_bytes_deserializable():
    model = _build_linear_model()
    raw = ir_to_bytes(model)
    msg = pb2.OMLEModel()
    msg.ParseFromString(raw)
    assert msg.metadata.name == "linear_iris"


# ── proto_to_ir (round-trip) ──────────────────────────────────────────────────

def test_proto_roundtrip_linear(proto_json):
    original = _build_linear_model()
    proto_msg = ir_to_proto(original)
    _print_proto_json(proto_msg, "Linear model round-trip proto JSON", proto_json)
    recovered = proto_to_ir(proto_msg)

    assert recovered.metadata.name == original.metadata.name
    assert len(recovered.inputs) == len(original.inputs)
    assert recovered.inputs[0].name == "X"
    assert len(recovered.nodes) == 1
    node = recovered.nodes[0]
    assert node.linear is not None
    assert node.linear.coefficients.tensor_ref.id == "coef"
    assert node.linear.post_transform == PostTransform.SOFTMAX


def test_proto_roundtrip_tree_ensemble(proto_json):
    original = _build_tree_ensemble_model()
    recovered = proto_to_ir(ir_to_proto(original))
    _print_proto_json(ir_to_proto(original), "TreeEnsemble round-trip proto JSON", proto_json)

    node = recovered.nodes[0]
    assert node.tree_ensemble is not None
    assert len(node.tree_ensemble.trees) == 1
    assert node.tree_ensemble.aggregation == TreeAggregation.SUM
    assert abs(node.tree_ensemble.base_scores.tensor.float64_data[0] - 0.5) < 1e-9


def test_proto_roundtrip_metadata(proto_json):
    original = _build_linear_model()
    recovered = proto_to_ir(ir_to_proto(original))

    assert recovered.metadata.format_version == "0.1.0"
    assert recovered.metadata.producer == "test"
    assert recovered.metadata.source_frameworks[0].name == "scikit-learn"


def test_proto_roundtrip_tensor_entries(proto_json):
    original = _build_linear_model()
    recovered = proto_to_ir(ir_to_proto(original))
    _print_proto_json(ir_to_proto(original), "Tensor entries round-trip proto JSON", proto_json)

    assert len(recovered.tensor_entries) == 2
    coef_entry = next(e for e in recovered.tensor_entries if e.id == "coef")
    assert coef_entry is not None
    assert len(coef_entry.dense.float32_data) == 12


def test_proto_roundtrip_model_schema(proto_json):
    original = _build_linear_model()
    recovered = proto_to_ir(ir_to_proto(original))

    assert recovered.model_schema is not None
    assert len(recovered.model_schema.features) == 1
    assert recovered.model_schema.features[0].name == "sl"
    assert len(recovered.model_schema.targets) == 1
    labels = [s.string_value for s in recovered.model_schema.targets[0].class_labels]
    assert labels == ["setosa", "versicolor", "virginica"]

def test_int64_fields_survive_a_proto_roundtrip():
    """int64 fields must come back as ints, not strings.

    proto_to_ir delegates to MessageToJson, and protobuf's canonical JSON mapping
    encodes 64-bit integers as strings. Without coercion in from_dict, a loaded
    model carried shape=['-1'] and re-serializing it raised
    TypeError: 'str' object cannot be interpreted as an integer.
    """
    model = OMLEModel(
        metadata=ModelMetadata(format_version="0.1.0", name="int64"),
        inputs=[InputSpec(name="X", type=TensorType(dtype=DataType.FLOAT32, shape=[-1, 4]))],
        outputs=[OutputSpec(name="y", type=TensorType(dtype=DataType.FLOAT32, shape=[-1]),
                            role=OutputRole.PREDICTION)],
    )
    recovered = proto_to_ir(ir_to_proto(model))

    for spec in list(recovered.inputs) + list(recovered.outputs):
        assert all(isinstance(d, int) for d in spec.type.shape), spec.type.shape
    assert recovered.inputs[0].type.shape == [-1, 4]
    assert recovered.outputs[0].type.shape == [-1]

    # The load → save path must not raise.
    assert ir_to_proto(recovered).SerializeToString() == ir_to_proto(model).SerializeToString()
