"""Tests for IR construction, to_dict/from_dict round-trips, and basic usage."""

import pytest

import omle
from omle import (
    DataType,
    Expression,
    Feature,
    InputSpec,
    Linear,
    MeasureLevel,
    ModelMetadata,
    ModelSchema,
    NameRange,
    NamespaceImport,
    Node,
    NodeInput,
    NodeOutput,
    OMLEModel,
    OutputRole,
    OutputSpec,
    PostTransform,
    Predicate,
    Scalar,
    SimplePredicateOperator,
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

# ── Scalar ────────────────────────────────────────────────────────────────────

def test_scalar_bool():
    s = Scalar.bool(True)
    assert s.bool_value is True
    assert s.value is True
    d = s.to_dict()
    assert Scalar.from_dict(d).bool_value is True


def test_scalar_int():
    s = Scalar.int(42)
    assert s.int_value == 42
    rt = Scalar.from_dict(s.to_dict())
    assert rt.int_value == 42


def test_scalar_float():
    s = Scalar.float(3.14)
    rt = Scalar.from_dict(s.to_dict())
    assert abs(rt.double_value - 3.14) < 1e-10


def test_scalar_string():
    s = Scalar.string("hello")
    rt = Scalar.from_dict(s.to_dict())
    assert rt.string_value == "hello"


def test_scalar_only_one_field():
    with pytest.raises(ValueError):
        Scalar(int_value=1, double_value=2.0)


# ── TensorType ────────────────────────────────────────────────────────────────

def test_tensor_type_roundtrip():
    tt = TensorType(dtype=DataType.FLOAT32, shape=[-1, 10])
    rt = TensorType.from_dict(tt.to_dict())
    assert rt.dtype == DataType.FLOAT32
    assert rt.shape == [-1, 10]


# ── Tensor ────────────────────────────────────────────────────────────────────

def test_tensor_float32_roundtrip():
    t = Tensor(
        name="weights",
        type=TensorType(dtype=DataType.FLOAT32, shape=[3]),
        float32_data=[0.1, 0.2, 0.3],
    )
    rt = Tensor.from_dict(t.to_dict())
    assert rt.name == "weights"
    assert len(rt.float32_data) == 3


def test_tensor_raw_data_roundtrip():
    t = Tensor(name="raw", raw_data=b"\x01\x02\x03")
    rt = Tensor.from_dict(t.to_dict())
    assert rt.raw_data == b"\x01\x02\x03"


# ── Expression ────────────────────────────────────────────────────────────────

def test_expression_column():
    e = Expression.from_ref("age")
    rt = Expression.from_dict(e.to_dict())
    assert rt.ref == "age"


def test_expression_literal():
    e = Expression.from_literal(Scalar.float(1.0))
    rt = Expression.from_dict(e.to_dict())
    assert rt.literal.double_value == 1.0


def test_expression_apply():
    e = Expression.from_apply("log", Expression.from_ref("x"))
    rt = Expression.from_dict(e.to_dict())
    assert rt.apply.function == "log"
    assert rt.apply.arguments[0].ref == "x"


# ── Predicate ─────────────────────────────────────────────────────────────────

def test_predicate_true():
    p = Predicate.true()
    rt = Predicate.from_dict(p.to_dict())
    assert rt.true_predicate is not None


def test_predicate_compare():
    p = Predicate.compare("age", SimplePredicateOperator.GREATER_THAN, Scalar.float(18.0))
    rt = Predicate.from_dict(p.to_dict())
    assert rt.simple.column == "age"
    assert rt.simple.op == SimplePredicateOperator.GREATER_THAN
    assert rt.simple.value.double_value == 18.0


def test_predicate_and():
    p = Predicate.and_(
        Predicate.compare("x", SimplePredicateOperator.GREATER_THAN, Scalar.int(0)),
        Predicate.compare("x", SimplePredicateOperator.LESS_THAN, Scalar.int(100)),
    )
    rt = Predicate.from_dict(p.to_dict())
    assert len(rt.compound.predicates) == 2


# ── NameRange ─────────────────────────────────────────────────────────────────

def test_name_range_expand():
    nr = NameRange(prefix="f", start=0, end=5)
    assert nr.expand() == ["f0", "f1", "f2", "f3", "f4"]


def test_name_range_expand_padded():
    nr = NameRange(prefix="f", start=0, end=3, width=3)
    assert nr.expand() == ["f000", "f001", "f002"]


# ── Feature ───────────────────────────────────────────────────────────────────

def test_feature_roundtrip():
    f = Feature(
        name="age",
        type=TensorType(dtype=DataType.FLOAT64, shape=[-1]),
        measure_level=MeasureLevel.CONTINUOUS,
        source="X",
        index=0,
    )
    rt = Feature.from_dict(f.to_dict())
    assert rt.name == "age"
    assert rt.measure_level == MeasureLevel.CONTINUOUS
    assert rt.source == "X"


def test_feature_range():
    f = Feature(range=NameRange(prefix="f", start=0, end=100), source="X")
    assert f.expand_names() == [f"f{i}" for i in range(100)]


# ── Linear body ───────────────────────────────────────────────────────────────

def test_linear_roundtrip():
    lin = Linear(
        coefficients=TensorValue.of_ref(TensorRef(id="coef")),
        intercept=TensorValue.of_tensor(Tensor(float64_data=[0.5])),
        post_transform=PostTransform.SIGMOID,
    )
    rt = Linear.from_dict(lin.to_dict())
    assert rt.coefficients.tensor_ref.id == "coef"
    assert rt.intercept.tensor.float64_data == [0.5]
    assert rt.post_transform == PostTransform.SIGMOID


# ── Tree body ─────────────────────────────────────────────────────────────────

def test_tree_roundtrip():
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
        leaf_value=TensorValue.of_tensor(Tensor(float64_data=[0.0, 1.0, 0.0])),
    )
    rt = Tree.from_dict(tree.to_dict())
    assert rt.num_nodes == 3
    assert rt.node_kind[0] == TreeNodeKind.BRANCH
    assert rt.split_threshold.tensor == Tensor(float64_data=[0.5])


# ── TreeEnsemble body ─────────────────────────────────────────────────────────

def test_tree_ensemble_roundtrip():
    te = TreeEnsemble(
        trees=[Tree(num_nodes=1, node_kind=[TreeNodeKind.LEAF],
                    leaf_value=TensorValue.of_tensor(Tensor(float64_data=[1.0])))],
        aggregation=TreeAggregation.SUM,
        post_transform=PostTransform.SIGMOID,
        base_scores=TensorValue.of_tensor(Tensor(float64_data=[0.5])),
    )
    rt = TreeEnsemble.from_dict(te.to_dict())
    assert len(rt.trees) == 1
    assert rt.aggregation == TreeAggregation.SUM
    assert rt.base_scores.tensor.float64_data == [0.5]


# ── Node ──────────────────────────────────────────────────────────────────────

def test_node_with_linear():
    node = Node(
        name="linear_node",
        domain="omle.ml",
        op="LinearClassifier",
        inputs=[NodeInput(name="X")],
        outputs=[NodeOutput(name="prediction", role=OutputRole.PREDICTION)],
        linear=Linear(coefficients=TensorValue.of_ref(TensorRef(id="coef"))),
    )
    rt = Node.from_dict(node.to_dict())
    assert rt.name == "linear_node"
    assert rt.linear is not None
    assert rt.linear.coefficients.tensor_ref.id == "coef"
    assert rt.outputs[0].role == OutputRole.PREDICTION


# ── Full model round-trip ─────────────────────────────────────────────────────

def _build_sample_model() -> OMLEModel:
    return OMLEModel(
        metadata=ModelMetadata(
            format_version="0.1.0",
            name="sample",
            producer="test",
            source_frameworks=[SourceFramework(name="scikit-learn")],
        ),
        operator_imports=[NamespaceImport(namespace="omle.ml", version="0.1")],
        inputs=[InputSpec(name="X", type=TensorType(dtype=DataType.FLOAT32, shape=[-1, 4]))],
        outputs=[OutputSpec(
            name="y_pred",
            type=TensorType(dtype=DataType.FLOAT32, shape=[-1]),
            role=OutputRole.PREDICTION,
        )],
        model_schema=ModelSchema(
            features=[
                Feature(name="sepal_length", source="X", index=0,
                        type=TensorType(dtype=DataType.FLOAT32, shape=[-1]),
                        measure_level=MeasureLevel.CONTINUOUS),
                Feature(name="sepal_width", source="X", index=1,
                        type=TensorType(dtype=DataType.FLOAT32, shape=[-1]),
                        measure_level=MeasureLevel.CONTINUOUS),
            ],
            targets=[
                Target(name="species", kind=TargetKind.MULTICLASS,
                       class_labels=[Scalar.string("setosa"), Scalar.string("versicolor"),
                                     Scalar.string("virginica")])
            ],
        ),
        tensor_entries=[
            TensorEntry(id="coef", dense=Tensor(name="coef",
                type=TensorType(dtype=DataType.FLOAT32, shape=[4]),
                float32_data=[0.1, 0.2, -0.3, 0.05])),
            TensorEntry(id="bias", dense=Tensor(name="bias",
                type=TensorType(dtype=DataType.FLOAT32, shape=[1]),
                float32_data=[0.5])),
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


def test_model_to_dict_from_dict():
    model = _build_sample_model()
    d = model.to_dict()
    rt = OMLEModel.from_dict(d)

    assert rt.metadata.name == "sample"
    assert rt.metadata.source_frameworks[0].name == "scikit-learn"
    assert len(rt.inputs) == 1
    assert rt.inputs[0].name == "X"
    assert len(rt.outputs) == 1
    assert rt.outputs[0].name == "y_pred"
    assert rt.model_schema is not None
    assert len(rt.model_schema.features) == 2
    assert len(rt.tensor_entries) == 2
    assert len(rt.nodes) == 1
    node = rt.nodes[0]
    assert node.linear is not None
    assert node.linear.post_transform == PostTransform.SOFTMAX


def test_model_json_roundtrip(tmp_path):
    model = _build_sample_model()
    path = tmp_path / "model.json"
    omle.save_json(model, path)
    rt = omle.load_json(path)
    assert rt.metadata.name == "sample"
    assert rt.nodes[0].linear.post_transform == PostTransform.SOFTMAX


def test_model_to_json_string():
    model = _build_sample_model()
    text = omle.to_json(model)
    rt = omle.from_json(text)
    assert rt.metadata.name == "sample"


def test_model_load_auto_dispatch(tmp_path):
    model = _build_sample_model()
    path = tmp_path / "model.json"
    omle.save(model, path)
    rt = omle.load(path)
    assert rt.metadata.name == "sample"


def test_model_accessor_helpers():
    model = _build_sample_model()
    assert model.get_tensor_entry("coef") is not None
    assert model.get_tensor_entry("nonexistent") is None
    assert model.get_node("clf") is not None
    assert "X" in model.input_names()
    assert "y_pred" in model.output_names()
    assert "y_pred" in model.node_output_names()
