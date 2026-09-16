"""Tests for the ModelValidator."""

import pytest

from omle import (
    DataType,
    DefineFunction,
    Expression,
    Feature,
    FunctionParameter,
    InputSpec,
    ModelMetadata,
    ModelSchema,
    NameRange,
    Node,
    NodeInput,
    NodeOutput,
    OMLEModel,
    OutputRole,
    OutputSpec,
    Scalar,
    TensorRef,
    assert_valid,
    validate,
)


def _minimal_valid_model() -> OMLEModel:
    return OMLEModel(
        metadata=ModelMetadata(format_version="0.1.0", name="test"),
        inputs=[InputSpec(name="X")],
        outputs=[OutputSpec(name="X", role=OutputRole.PREDICTION)],
    )


# ── metadata ──────────────────────────────────────────────────────────────────

def test_valid_minimal_model():
    result = validate(_minimal_valid_model())
    assert result.is_valid, str(result)


def test_missing_format_version():
    model = _minimal_valid_model()
    model.metadata.format_version = ""
    result = validate(model)
    assert not result.is_valid
    assert any("format_version" in e.path for e in result.errors)


# ── inputs ────────────────────────────────────────────────────────────────────

def test_duplicate_input_names():
    model = _minimal_valid_model()
    model.inputs = [InputSpec(name="X"), InputSpec(name="X")]
    result = validate(model)
    assert not result.is_valid
    assert any("Duplicate input" in e.message for e in result.errors)


def test_empty_input_name():
    model = _minimal_valid_model()
    model.inputs = [InputSpec(name="")]
    result = validate(model)
    assert not result.is_valid


# ── outputs ───────────────────────────────────────────────────────────────────

def test_output_resolves_to_input():
    model = _minimal_valid_model()
    result = validate(model)
    assert result.is_valid


def test_output_does_not_resolve():
    model = _minimal_valid_model()
    model.outputs = [OutputSpec(name="nonexistent")]
    result = validate(model)
    assert not result.is_valid
    assert any("does not resolve" in e.message for e in result.errors)


def test_output_resolves_to_node_output():
    model = _minimal_valid_model()
    model.nodes = [
        Node(
            name="n1",
            outputs=[NodeOutput(name="prediction")],
            inputs=[NodeInput(name="X")],
        )
    ]
    model.outputs = [OutputSpec(name="prediction")]
    result = validate(model)
    assert result.is_valid


# ── name ranges ───────────────────────────────────────────────────────────────

def test_name_range_negative_start():
    model = _minimal_valid_model()
    model.model_schema = ModelSchema(
        features=[Feature(range=NameRange(prefix="f", start=-1, end=10), source="X")]
    )
    result = validate(model)
    assert not result.is_valid
    assert any("start" in e.message for e in result.errors)


def test_name_range_end_less_than_start():
    model = _minimal_valid_model()
    model.model_schema = ModelSchema(
        features=[Feature(range=NameRange(prefix="f", start=5, end=3), source="X")]
    )
    result = validate(model)
    assert not result.is_valid
    assert any("end" in e.message for e in result.errors)


# ── features ──────────────────────────────────────────────────────────────────

def test_duplicate_feature_names():
    model = _minimal_valid_model()
    model.model_schema = ModelSchema(
        features=[
            Feature(name="age", source="X"),
            Feature(name="age", source="X"),
        ]
    )
    result = validate(model)
    assert not result.is_valid
    assert any("Duplicate feature" in e.message for e in result.errors)


def test_feature_unknown_source():
    model = _minimal_valid_model()
    model.model_schema = ModelSchema(
        features=[Feature(name="age", source="nonexistent")]
    )
    result = validate(model)
    assert not result.is_valid
    assert any("Source" in e.message for e in result.errors)


# ── nodes ─────────────────────────────────────────────────────────────────────

def test_duplicate_node_names():
    model = _minimal_valid_model()
    model.nodes = [
        Node(name="n1", inputs=[NodeInput(name="X")],
             outputs=[NodeOutput(name="out1")]),
        Node(name="n1", inputs=[NodeInput(name="X")],
             outputs=[NodeOutput(name="out2")]),
    ]
    result = validate(model)
    assert not result.is_valid
    assert any("Duplicate node" in e.message for e in result.errors)


def test_empty_node_name():
    model = _minimal_valid_model()
    model.nodes = [Node(name="", outputs=[NodeOutput(name="out")])]
    result = validate(model)
    assert not result.is_valid


def test_duplicate_node_output_names():
    model = _minimal_valid_model()
    model.nodes = [
        Node(
            name="n1",
            inputs=[NodeInput(name="X")],
            outputs=[NodeOutput(name="dup"), NodeOutput(name="dup")],
        )
    ]
    result = validate(model)
    assert not result.is_valid
    assert any("Duplicate NodeOutput" in e.message for e in result.errors)


def test_dag_cycle_detection():
    """Two nodes that depend on each other form a cycle."""
    model = _minimal_valid_model()
    model.nodes = [
        Node(name="a", inputs=[NodeInput(name="b_out")],
             outputs=[NodeOutput(name="a_out")]),
        Node(name="b", inputs=[NodeInput(name="a_out")],
             outputs=[NodeOutput(name="b_out")]),
    ]
    result = validate(model)
    assert not result.is_valid
    assert any("cycle" in e.message.lower() for e in result.errors)


# ── constants ─────────────────────────────────────────────────────────────────

def test_duplicate_constant_names():
    from omle import Tensor, TensorEntry
    model = _minimal_valid_model()
    model.tensor_entries = [
        TensorEntry(id="w", dense=Tensor(name="w", float32_data=[1.0])),
        TensorEntry(id="w", dense=Tensor(name="w", float32_data=[2.0])),
    ]
    result = validate(model)
    assert not result.is_valid
    assert any("Duplicate constant" in e.message for e in result.errors)


# ── functions ─────────────────────────────────────────────────────────────────

def test_duplicate_function_names():
    model = _minimal_valid_model()
    model.functions = [
        DefineFunction(name="double", body=Expression.from_ref("x")),
        DefineFunction(name="double", body=Expression.from_ref("x")),
    ]
    result = validate(model)
    assert not result.is_valid
    assert any("Duplicate function" in e.message for e in result.errors)


def test_function_self_recursion():
    model = _minimal_valid_model()
    # f(x) = f(x) — direct self-recursion
    model.functions = [
        DefineFunction(
            name="f",
            parameters=[FunctionParameter(name="x", data_type=DataType.FLOAT64)],
            body=Expression.from_apply("f", Expression.from_ref("x")),
        )
    ]
    result = validate(model)
    assert not result.is_valid
    assert any("recursive" in e.message.lower() for e in result.errors)


def test_duplicate_function_parameters():
    model = _minimal_valid_model()
    model.functions = [
        DefineFunction(
            name="f",
            parameters=[
                FunctionParameter(name="x"),
                FunctionParameter(name="x"),
            ],
            body=Expression.from_ref("x"),
        )
    ]
    result = validate(model)
    assert not result.is_valid
    assert any("Duplicate parameter" in e.message for e in result.errors)


# ── assert_valid ──────────────────────────────────────────────────────────────

def test_assert_valid_passes():
    assert_valid(_minimal_valid_model())


def test_assert_valid_raises():
    model = _minimal_valid_model()
    model.outputs = [OutputSpec(name="does_not_exist")]
    with pytest.raises(ValueError, match="Validation failed"):
        assert_valid(model)


# ── verification ──────────────────────────────────────────────────────────────

def _model_with_tensor_entry(tensor_name: str, entry_id: str):
    from omle import Tensor, TensorEntry
    model = _minimal_valid_model()
    model.inputs  = [InputSpec(name="X")]
    model.outputs = [OutputSpec(name="X", role=OutputRole.PREDICTION)]
    model.tensor_entries = [
        TensorEntry(id=entry_id, dense=Tensor(name=tensor_name, float32_data=[1.0, 2.0]))
    ]
    return model


def test_verification_valid():
    from omle.ir.verification import (
        ModelVerification,
        NumericTolerance,
        VerificationCase,
    )
    model = _model_with_tensor_entry("X", "inp0")
    model.verification = ModelVerification(
        cases=[VerificationCase(
            inputs=[TensorRef(id="inp0")],
            expected_outputs=[TensorRef(id="inp0")],
        )],
        tolerance=NumericTolerance(atol=1e-5, rtol=1e-4),
    )
    result = validate(model)
    assert result.is_valid, str(result)


def test_verification_bad_tensor_ref():
    from omle.ir.verification import ModelVerification, VerificationCase
    model = _model_with_tensor_entry("X", "inp0")
    model.verification = ModelVerification(
        cases=[VerificationCase(inputs=[TensorRef(id="missing")])]
    )
    result = validate(model)
    assert not result.is_valid
    assert any("does not match any tensor_entry" in e.message for e in result.errors)


def test_verification_inner_name_mismatch():
    from omle.ir.verification import ModelVerification, VerificationCase
    model = _model_with_tensor_entry("wrong_name", "inp0")
    model.verification = ModelVerification(
        cases=[VerificationCase(inputs=[TensorRef(id="inp0")])]
    )
    result = validate(model)
    assert not result.is_valid
    assert any("inner name" in e.message for e in result.errors)


def test_verification_negative_tolerance():
    from omle.ir.verification import ModelVerification, NumericTolerance
    model = _minimal_valid_model()
    model.verification = ModelVerification(
        tolerance=NumericTolerance(atol=-0.1)
    )
    result = validate(model)
    assert not result.is_valid
    assert any("atol" in e.message for e in result.errors)


def test_verification_scalar_tolerance():
    """Tolerances arriving as Scalar messages (as converters emit them) validate."""
    from omle.ir.verification import ModelVerification, NumericTolerance
    model = _minimal_valid_model()
    model.verification = ModelVerification(
        tolerance=NumericTolerance(atol=Scalar.float(1e-4), rtol=Scalar.float(1e-4))
    )
    assert validate(model).is_valid


def test_verification_negative_scalar_tolerance():
    from omle.ir.verification import ModelVerification, NumericTolerance
    model = _minimal_valid_model()
    model.verification = ModelVerification(tolerance=NumericTolerance(atol=Scalar.float(-0.1)))
    result = validate(model)
    assert not result.is_valid
    assert any("atol" in e.message for e in result.errors)


def test_verification_non_numeric_tolerance():
    from omle.ir.verification import ModelVerification, NumericTolerance
    model = _minimal_valid_model()
    model.verification = ModelVerification(tolerance=NumericTolerance(atol=Scalar.string("tight")))
    result = validate(model)
    assert not result.is_valid
    assert any("atol" in e.message for e in result.errors)


# ── warmup ────────────────────────────────────────────────────────────────────

def test_warmup_valid():
    from omle.ir.verification import RuntimeWarmup, WarmupCase
    model = _model_with_tensor_entry("X", "inp0")
    model.warmup = RuntimeWarmup(
        cases=[WarmupCase(inputs=[TensorRef(id="inp0")], repeat=3)]
    )
    result = validate(model)
    assert result.is_valid, str(result)


def test_warmup_negative_repeat():
    from omle.ir.verification import RuntimeWarmup, WarmupCase
    model = _minimal_valid_model()
    model.warmup = RuntimeWarmup(cases=[WarmupCase(repeat=-1)])
    result = validate(model)
    assert not result.is_valid
    assert any("repeat" in e.message for e in result.errors)


def test_warmup_bad_tensor_ref():
    from omle.ir.verification import RuntimeWarmup, WarmupCase
    model = _minimal_valid_model()
    model.warmup = RuntimeWarmup(
        cases=[WarmupCase(inputs=[TensorRef(id="no_such_entry")])]
    )
    result = validate(model)
    assert not result.is_valid
    assert any("does not match any tensor_entry" in e.message for e in result.errors)


# ── sample_inputs ─────────────────────────────────────────────────────────────

def test_sample_inputs_valid():
    from omle.ir.verification import SampleInputCase, SampleInputSet
    model = _model_with_tensor_entry("X", "inp0")
    model.sample_inputs = SampleInputSet(
        cases=[SampleInputCase(inputs=[TensorRef(id="inp0")], description="example")]
    )
    result = validate(model)
    assert result.is_valid, str(result)


def test_sample_inputs_bad_tensor_ref():
    from omle.ir.verification import SampleInputCase, SampleInputSet
    model = _minimal_valid_model()
    model.sample_inputs = SampleInputSet(
        cases=[SampleInputCase(inputs=[TensorRef(id="ghost")])]
    )
    result = validate(model)
    assert not result.is_valid
    assert any("does not match any tensor_entry" in e.message for e in result.errors)
