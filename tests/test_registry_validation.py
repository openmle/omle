"""Tests for registry-based validation (operators.v1.json + functions.v1.json)."""


from omle import (
    Apply,
    Attribute,
    DataType,
    DefineFunction,
    Expression,
    FunctionParameter,
    InputSpec,
    Linear,
    ModelMetadata,
    NamespaceImport,
    Node,
    NodeInput,
    NodeOutput,
    OMLEModel,
    OutputRole,
    OutputSpec,
    Scalar,
    Tensor,
    TensorEntry,
    TensorRef,
    TensorType,
    validate,
)
from omle.registry import (
    load_function_registry,
    load_operator_registry,
)

# ── Registry loading ──────────────────────────────────────────────────────────

def test_operator_registry_loads():
    reg = load_operator_registry()
    assert reg.known_namespace("omle.core")
    assert reg.known_namespace("omle.feature")
    assert reg.known_namespace("omle.ml")


def test_operator_registry_known_ops():
    reg = load_operator_registry()
    assert reg.get("omle.core", "Identity") is not None
    assert reg.get("omle.core", "Cast") is not None
    assert reg.get("omle.core", "Split") is not None
    assert reg.get("omle.feature", "StandardScaler") is not None
    assert reg.get("omle.feature", "OneHotEncoder") is not None
    assert reg.get("omle.feature", "Imputer") is not None
    assert reg.get("omle.feature", "Binarizer") is not None
    assert reg.get("omle.feature", "Bucketizer") is not None
    assert reg.get("omle.feature", "Discretizer") is not None
    assert reg.get("omle.feature", "LabelEncoder") is not None
    assert reg.get("omle.feature", "NormDiscrete") is not None
    assert reg.get("omle.feature", "MapValues") is not None
    assert reg.get("omle.ml", "Linear") is not None
    assert reg.get("omle.ml", "TreeEnsemble") is not None


def test_operator_registry_unknown_op():
    reg = load_operator_registry()
    assert reg.get("omle.core", "DoesNotExist") is None


def test_function_registry_loads():
    reg = load_function_registry()
    assert reg.known_namespace("omle.functions")


def test_function_registry_known_functions():
    reg = load_function_registry()
    for name in ("add", "sub", "mul", "div", "log", "exp", "sqrt",
                 "if", "coalesce", "is_missing", "map_values",
                 "equal", "less_than", "and", "or", "not",
                 "concat", "lower", "upper", "trim",
                 "in", "not_in", "cast"):
        assert reg.get("omle.functions", name) is not None, f"Missing function: {name}"


def test_function_registry_arity():
    reg = load_function_registry()
    add = reg.get("omle.functions", "add")
    assert add.min_args == 2
    assert add.max_args == 2
    assert not add.is_variadic

    log_ = reg.get("omle.functions", "log")
    assert log_.min_args == 1
    assert log_.max_args == 1

    coalesce = reg.get("omle.functions", "coalesce")
    assert coalesce.min_args == 1   # x1 required, x2 variadic (min 0 extra)
    assert coalesce.is_variadic

    map_values = reg.get("omle.functions", "map_values")
    assert map_values.min_args == 1   # x required, pairs variadic
    assert map_values.is_variadic


def test_function_registry_resolve_unqualified():
    reg = load_function_registry()
    fn = reg.resolve("log", ["omle.functions"])
    assert fn is not None
    assert fn.name == "log"


def test_function_registry_resolve_unknown():
    reg = load_function_registry()
    assert reg.resolve("does_not_exist", ["omle.functions"]) is None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _base_model(**kwargs) -> OMLEModel:
    return OMLEModel(
        metadata=ModelMetadata(format_version="0.1.0", name="test"),
        inputs=[InputSpec(name="X")],
        outputs=kwargs.pop("outputs", [OutputSpec(name="X", role=OutputRole.PREDICTION)]),
        **kwargs,
    )


def _attr(name: str, **kw) -> Attribute:
    return Attribute(name=name, **kw)


# ── Operator import declaration ───────────────────────────────────────────────

def test_undeclared_operator_namespace():
    model = _base_model(
        nodes=[Node(name="n1", domain="omle.core", op="Identity",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="y")])],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert not result.is_valid
    assert any("operator_imports" in e.message for e in result.errors)


def test_declared_operator_namespace_passes():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.core", version="0.1")],
        nodes=[Node(name="n1", domain="omle.core", op="Identity",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="y")])],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert result.is_valid, str(result)


# ── Unknown operator ──────────────────────────────────────────────────────────

def test_unknown_operator_in_known_namespace():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.core", version="0.1")],
        nodes=[Node(name="n1", domain="omle.core", op="Nonexistent",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="y")])],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert not result.is_valid
    assert any("Unknown operator" in e.message for e in result.errors)


def test_vendor_namespace_skipped():
    """Custom/vendor namespaces are not validated against the registry."""
    model = _base_model(
        nodes=[Node(name="n1", domain="vendor.custom", op="MyOp",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="y")])],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    # Should be valid (no registry check for unknown namespace)
    assert result.is_valid, str(result)


# ── Required attributes ───────────────────────────────────────────────────────

def test_cast_missing_required_attribute():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.core", version="0.1")],
        nodes=[Node(name="n1", domain="omle.core", op="Cast",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="y")],
                    attributes=[])],   # missing output_dtype
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert not result.is_valid
    assert any("output_dtype" in e.message for e in result.errors)


def test_cast_with_required_attribute_passes():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.core", version="0.1")],
        nodes=[Node(name="n1", domain="omle.core", op="Cast",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="y")],
                    attributes=[_attr("output_dtype", s="FLOAT32")])],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert result.is_valid, str(result)


# ── Enum attribute values ─────────────────────────────────────────────────────

def test_normalizer_invalid_norm_enum():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.feature", version="0.1")],
        nodes=[Node(name="n1", domain="omle.feature", op="Normalizer",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="y")],
                    attributes=[_attr("norm", s="l99")])],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert not result.is_valid
    assert any("norm" in e.message and "l99" in e.message for e in result.errors)


def test_normalizer_valid_norm_enum():
    for norm in ("l1", "l2", "max"):
        model = _base_model(
            operator_imports=[NamespaceImport(namespace="omle.feature", version="0.1")],
            nodes=[Node(name="n1", domain="omle.feature", op="Normalizer",
                        inputs=[NodeInput(name="X")],
                        outputs=[NodeOutput(name="y")],
                        attributes=[_attr("norm", s=norm)])],
            outputs=[OutputSpec(name="y")],
        )
        result = validate(model)
        assert result.is_valid, f"norm={norm!r}: {result}"


# ── Structured operators: body field required ─────────────────────────────────

def test_ml_linear_missing_body():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.ml", version="0.1")],
        nodes=[Node(name="clf", domain="omle.ml", op="Linear",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="y")])],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert not result.is_valid
    assert any("linear" in e.message for e in result.errors)


def test_ml_linear_with_body_passes():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.ml", version="0.1")],
        nodes=[Node(name="clf", domain="omle.ml", op="Linear",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="y")],
                    linear=Linear(coefficients=TensorRef(id="coef")))],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert result.is_valid, str(result)


def test_ml_tree_ensemble_missing_body():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.ml", version="0.1")],
        nodes=[Node(name="te", domain="omle.ml", op="TreeEnsemble",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="y")])],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert not result.is_valid
    assert any("tree_ensemble" in e.message for e in result.errors)


# ── Split operator ────────────────────────────────────────────────────────────

def test_split_output_count_mismatch():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.core", version="0.1")],
        nodes=[Node(name="s1", domain="omle.core", op="Split",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="a"), NodeOutput(name="b")],
                    attributes=[_attr("sections", ints=[3, 3, 4])])],  # 3 sections, 2 outputs
        outputs=[OutputSpec(name="a")],
    )
    result = validate(model)
    assert not result.is_valid
    assert any("Split" in e.message and "outputs" in e.message for e in result.errors)


def test_split_negative_section():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.core", version="0.1")],
        nodes=[Node(name="s1", domain="omle.core", op="Split",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="a"), NodeOutput(name="b")],
                    attributes=[_attr("sections", ints=[5, -1])])],
        outputs=[OutputSpec(name="a")],
    )
    result = validate(model)
    assert not result.is_valid
    assert any("positive" in e.message for e in result.errors)


def test_split_valid():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.core", version="0.1")],
        nodes=[Node(name="s1", domain="omle.core", op="Split",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="a"), NodeOutput(name="b"), NodeOutput(name="c")],
                    attributes=[_attr("sections", ints=[3, 3, 4])])],
        outputs=[OutputSpec(name="a")],
    )
    result = validate(model)
    assert result.is_valid, str(result)


# ── Impute operator ───────────────────────────────────────────────────────────

def test_impute_no_fill():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.feature", version="0.1")],
        nodes=[Node(name="imp", domain="omle.feature", op="Imputer",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="y")],
                    attributes=[])],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert not result.is_valid
    assert any("Impute" in e.message for e in result.errors)


def test_impute_both_fills():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.feature", version="0.1")],
        nodes=[Node(name="imp", domain="omle.feature", op="Imputer",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="y")],
                    attributes=[
                        _attr("fill_value", f64=0.0),
                        _attr("fill_tensor", tensor=TensorRef(id="fill")),
                    ])],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert not result.is_valid
    assert any("Impute" in e.message for e in result.errors)


def test_impute_fill_value_only():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.feature", version="0.1")],
        nodes=[Node(name="imp", domain="omle.feature", op="Imputer",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="y")],
                    attributes=[_attr("fill_value", f64=0.0)])],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert result.is_valid, str(result)


def test_impute_fill_tensor_only():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.feature", version="0.1")],
        nodes=[Node(name="imp", domain="omle.feature", op="Imputer",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="y")],
                    attributes=[_attr("fill_tensor", tensor=TensorRef(id="fill"))])],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert result.is_valid, str(result)


# ── OneHotEncode operator ─────────────────────────────────────────────────────

def _ohe_attrs(cats: list[str], id_prefix: str):
    """Build categories + category_offsets tensor entries and attributes for OneHotEncoder."""
    cats_entry = TensorEntry(
        id=f"{id_prefix}_cats",
        dense=Tensor(
            name=f"{id_prefix}_cats",
            type=TensorType(dtype=DataType.STRING, shape=[len(cats)]),
            string_data=cats,
        ),
    )
    offsets_entry = TensorEntry(
        id=f"{id_prefix}_offsets",
        dense=Tensor(
            name=f"{id_prefix}_offsets",
            type=TensorType(dtype=DataType.INT64, shape=[2]),
            int64_data=[0, len(cats)],
        ),
    )
    attrs = [
        _attr("categories", tensor_ref=TensorRef(id=cats_entry.id)),
        _attr("category_offsets", tensor_ref=TensorRef(id=offsets_entry.id)),
    ]
    return [cats_entry, offsets_entry], attrs


def test_ohe_shape_mismatch():
    entries, attrs = _ohe_attrs(["a", "b", "c"], "ohe")
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.feature", version="0.1")],
        nodes=[Node(name="ohe", domain="omle.feature", op="OneHotEncoder",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(
                        name="y",
                        type=TensorType(dtype=DataType.FLOAT32, shape=[-1, 5]),  # 5 cols
                    )],
                    attributes=attrs)],  # 3 cats
        tensor_entries=entries,
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert not result.is_valid
    assert any("OneHotEncode" in e.message for e in result.errors)


def test_ohe_shape_matches():
    entries, attrs = _ohe_attrs(["a", "b", "c"], "ohe")
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.feature", version="0.1")],
        nodes=[Node(name="ohe", domain="omle.feature", op="OneHotEncoder",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(
                        name="y",
                        type=TensorType(dtype=DataType.FLOAT32, shape=[-1, 3]),
                    )],
                    attributes=attrs)],
        tensor_entries=entries,
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert result.is_valid, str(result)


# ── Binarize operator ─────────────────────────────────────────────────────────

def test_binarize_missing_threshold():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.feature", version="0.1")],
        nodes=[Node(name="bin", domain="omle.feature", op="Binarizer",
                    inputs=[NodeInput(name="x0")],
                    outputs=[NodeOutput(name="y0")],
                    attributes=[])],
        outputs=[OutputSpec(name="y0")],
    )
    result = validate(model)
    assert not result.is_valid
    assert any("thresholds" in e.message for e in result.errors)


def test_binarize_with_threshold_passes():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.feature", version="0.1")],
        nodes=[Node(name="bin", domain="omle.feature", op="Binarizer",
                    inputs=[NodeInput(name="x0")],
                    outputs=[NodeOutput(name="y0")],
                    attributes=[_attr("thresholds", tensor=Tensor(
                        type=TensorType(dtype=DataType.FLOAT64, shape=[1]),
                        float64_data=[0.5],
                    ))])],
        outputs=[OutputSpec(name="y0")],
    )
    result = validate(model)
    assert result.is_valid, str(result)


# ── Bucketize operator ────────────────────────────────────────────────────────

def test_bucketize_missing_boundaries():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.feature", version="0.1")],
        nodes=[Node(name="bkt", domain="omle.feature", op="Bucketizer",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="y")],
                    attributes=[])],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert not result.is_valid
    assert any("boundaries" in e.message for e in result.errors)


def test_bucketize_with_boundaries_passes():
    bnd_entry = TensorEntry(
        id="bkt_boundaries",
        dense=Tensor(
            name="bkt_boundaries",
            type=TensorType(dtype=DataType.FLOAT64, shape=[3]),
            float64_data=[1.0, 2.0, 3.0],
        ),
    )
    off_entry = TensorEntry(
        id="bkt_offsets",
        dense=Tensor(
            name="bkt_offsets",
            type=TensorType(dtype=DataType.INT64, shape=[2]),
            int64_data=[0, 3],
        ),
    )
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.feature", version="0.1")],
        nodes=[Node(name="bkt", domain="omle.feature", op="Bucketizer",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="y")],
                    attributes=[
                        _attr("boundaries",      tensor_ref=TensorRef(id="bkt_boundaries")),
                        _attr("boundary_offsets", tensor_ref=TensorRef(id="bkt_offsets")),
                    ])],
        tensor_entries=[bnd_entry, off_entry],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert result.is_valid, str(result)


# ── LabelEncode operator ──────────────────────────────────────────────────────

def test_label_encode_missing_labels():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.feature", version="0.1")],
        nodes=[Node(name="le", domain="omle.feature", op="LabelEncoder",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="y")],
                    attributes=[])],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert not result.is_valid
    assert any("labels" in e.message for e in result.errors)


def test_label_encode_with_labels_passes():
    labels = ["cat", "dog", "fish"]
    labels_entry = TensorEntry(
        id="le_labels",
        dense=Tensor(
            name="le_labels",
            type=TensorType(dtype=DataType.STRING, shape=[len(labels)]),
            string_data=labels,
        ),
    )
    offsets_entry = TensorEntry(
        id="le_offsets",
        dense=Tensor(
            name="le_offsets",
            type=TensorType(dtype=DataType.INT64, shape=[2]),
            int64_data=[0, len(labels)],
        ),
    )
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.feature", version="0.1")],
        nodes=[Node(name="le", domain="omle.feature", op="LabelEncoder",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="y")],
                    attributes=[
                        _attr("labels", tensor=TensorRef(id="le_labels")),
                        _attr("label_offsets", tensor=TensorRef(id="le_offsets")),
                    ])],
        tensor_entries=[labels_entry, offsets_entry],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert result.is_valid, str(result)


# ── NormDiscrete operator ─────────────────────────────────────────────────────

def test_norm_discrete_missing_value():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.feature", version="0.1")],
        nodes=[Node(name="nd", domain="omle.feature", op="NormDiscrete",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="y")],
                    attributes=[])],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert not result.is_valid
    assert any("value" in e.message for e in result.errors)


def test_norm_discrete_with_value_passes():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.feature", version="0.1")],
        nodes=[Node(name="nd", domain="omle.feature", op="NormDiscrete",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="y")],
                    attributes=[_attr("value", s="cat")])],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert result.is_valid, str(result)


# ── MapValues operator ────────────────────────────────────────────────────────

def test_map_values_missing_required_attrs():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.feature", version="0.1")],
        nodes=[Node(name="mv", domain="omle.feature", op="MapValues",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="y")],
                    attributes=[])],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert not result.is_valid


def test_map_values_with_required_attrs_passes():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.feature", version="0.1")],
        nodes=[Node(name="mv", domain="omle.feature", op="MapValues",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="y")],
                    attributes=[
                        _attr("keys", tensor=TensorRef(id="keys")),
                        _attr("values", tensor=TensorRef(id="vals")),
                        _attr("output_dtype", s="FLOAT32"),
                    ])],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert result.is_valid, str(result)


# ── OrdinalEncoder with encoded_values ───────────────────────────────────────

def test_ordinal_encoder_with_encoded_values_passes():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.feature", version="0.1")],
        nodes=[Node(name="oe", domain="omle.feature", op="OrdinalEncoder",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="y")],
                    attributes=[
                        _attr("categories",       tensor=TensorRef(id="cats")),
                        _attr("category_offsets", tensor=TensorRef(id="offs")),
                        _attr("encoded_values",   tensor=TensorRef(id="vals")),
                        _attr("default_values",   tensor=TensorRef(id="unk")),
                    ])],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert result.is_valid, str(result)


def test_ordinal_encoder_without_encoded_values_passes():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.feature", version="0.1")],
        nodes=[Node(name="oe", domain="omle.feature", op="OrdinalEncoder",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="y")],
                    attributes=[
                        _attr("categories",       tensor=TensorRef(id="cats")),
                        _attr("category_offsets", tensor=TensorRef(id="offs")),
                    ])],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert result.is_valid, str(result)


# ── TargetEncoder required attributes ─────────────────────────────────────────

def test_target_encoder_with_required_attrs_passes():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.feature", version="0.1")],
        nodes=[Node(name="te", domain="omle.feature", op="TargetEncoder",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="y")],
                    attributes=[
                        _attr("categories",       tensor=TensorRef(id="cats")),
                        _attr("category_offsets", tensor=TensorRef(id="offs")),
                        _attr("encoded_values",   tensor=TensorRef(id="enc")),
                        _attr("default_values",   tensor=TensorRef(id="def")),
                        _attr("target_kind",      s="regression"),
                    ])],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert result.is_valid, str(result)


def test_target_encoder_missing_required_attrs_fails():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.feature", version="0.1")],
        nodes=[Node(name="te", domain="omle.feature", op="TargetEncoder",
                    inputs=[NodeInput(name="X")],
                    outputs=[NodeOutput(name="y")],
                    attributes=[])],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert not result.is_valid


# ── Function reference validation ─────────────────────────────────────────────

def _expr_node(fn_name: str, n_args: int) -> Node:
    """Node with a Derive operator whose expr attribute calls fn_name with n_args columns."""
    args = [Expression.from_ref(f"c{i}") for i in range(n_args)]
    return Node(
        name="derive",
        domain="omle.core",
        op="Derive",
        inputs=[NodeInput(name="X")],
        outputs=[NodeOutput(name="y")],
        attributes=[_attr("expr", expr=Expression(
            apply=Apply(function=fn_name, arguments=args)
        ))],
    )


def test_unknown_function_with_import():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.core", version="0.1")],
        function_imports=[NamespaceImport(namespace="omle.functions", version="0.1")],
        nodes=[_expr_node("totally_unknown_fn", 1)],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert not result.is_valid
    assert any("totally_unknown_fn" in e.message for e in result.errors)


def test_known_function_correct_args():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.core", version="0.1")],
        function_imports=[NamespaceImport(namespace="omle.functions", version="0.1")],
        nodes=[_expr_node("log", 1)],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert result.is_valid, str(result)


def test_function_too_few_args():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.core", version="0.1")],
        function_imports=[NamespaceImport(namespace="omle.functions", version="0.1")],
        nodes=[_expr_node("add", 1)],   # add requires 2 args
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert not result.is_valid
    assert any("add" in e.message and "2" in e.message for e in result.errors)


def test_function_too_many_args():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.core", version="0.1")],
        function_imports=[NamespaceImport(namespace="omle.functions", version="0.1")],
        nodes=[_expr_node("log", 3)],   # log requires exactly 1 arg
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert not result.is_valid
    assert any("log" in e.message and "1" in e.message for e in result.errors)


def test_variadic_function_many_args():
    """coalesce is variadic — any count >= 1 should be valid."""
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.core", version="0.1")],
        function_imports=[NamespaceImport(namespace="omle.functions", version="0.1")],
        nodes=[_expr_node("coalesce", 5)],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert result.is_valid, str(result)


def test_function_no_import_skips_check():
    """Without function_imports, unrecognised function names are allowed."""
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.core", version="0.1")],
        # no function_imports
        nodes=[_expr_node("my_custom_func", 2)],
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert result.is_valid, str(result)


# ── map_values pairs check ────────────────────────────────────────────────────

def _map_values_node(n_pair_elements: int) -> Node:
    """Node whose expr calls map_values with x + n_pair_elements extra args."""
    args = [Expression.from_ref("x")] + [
        Expression.from_literal(Scalar.int(i)) for i in range(n_pair_elements)
    ]
    return Node(
        name="derive",
        domain="omle.core",
        op="Derive",
        inputs=[NodeInput(name="X")],
        outputs=[NodeOutput(name="y")],
        attributes=[_attr("expr", expr=Expression(
            apply=Apply(function="map_values", arguments=args)
        ))],
    )


def test_map_values_odd_pairs():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.core", version="0.1")],
        function_imports=[NamespaceImport(namespace="omle.functions", version="0.1")],
        nodes=[_map_values_node(3)],   # x + 3 pair elements = odd
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert not result.is_valid
    assert any("map_values" in e.message and "even" in e.message for e in result.errors)


def test_map_values_even_pairs():
    model = _base_model(
        operator_imports=[NamespaceImport(namespace="omle.core", version="0.1")],
        function_imports=[NamespaceImport(namespace="omle.functions", version="0.1")],
        nodes=[_map_values_node(4)],   # x + 4 pair elements = even
        outputs=[OutputSpec(name="y")],
    )
    result = validate(model)
    assert result.is_valid, str(result)


# ── Function body validation ──────────────────────────────────────────────────

def test_function_body_unknown_call():
    model = _base_model(
        function_imports=[NamespaceImport(namespace="omle.functions", version="0.1")],
        functions=[
            DefineFunction(
                name="my_fn",
                parameters=[FunctionParameter(name="x", data_type=DataType.FLOAT64)],
                body=Expression(apply=Apply(
                    function="unknown_builtin",
                    arguments=[Expression.from_ref("x")],
                )),
            )
        ],
    )
    result = validate(model)
    assert not result.is_valid
    assert any("unknown_builtin" in e.message for e in result.errors)


def test_function_body_valid_call():
    model = _base_model(
        function_imports=[NamespaceImport(namespace="omle.functions", version="0.1")],
        functions=[
            DefineFunction(
                name="my_log",
                parameters=[FunctionParameter(name="x", data_type=DataType.FLOAT64)],
                body=Expression(apply=Apply(
                    function="log",
                    arguments=[Expression.from_ref("x")],
                )),
            )
        ],
    )
    result = validate(model)
    assert result.is_valid, str(result)
