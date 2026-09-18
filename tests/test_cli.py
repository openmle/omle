"""Tests for the CLI (omle validate / omle inspect)."""

import json

import pytest

from omle.cli import _build_parser, main

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def valid_model_file(tmp_path):
    """Write a valid model JSON and return its path."""
    import omle
    model = omle.OMLEModel(
        metadata=omle.ModelMetadata(
            format_version="0.1.0",
            name="iris_clf",
            producer="test",
            source_frameworks=[omle.SourceFramework(name="scikit-learn", version="1.4.0")],
            doc_string="Iris classification model",
        ),
        operator_imports=[omle.NamespaceImport(namespace="omle.ml", version="0.1")],
        function_imports=[omle.NamespaceImport(namespace="omle.functions", version="0.1")],
        inputs=[omle.InputSpec(
            name="X",
            type=omle.TensorType(dtype=omle.DataType.FLOAT32, shape=[-1, 4]),
        )],
        outputs=[
            omle.OutputSpec(name="y_pred", role=omle.OutputRole.PREDICTION),
            omle.OutputSpec(name="y_prob", role=omle.OutputRole.PROBABILITY),
        ],
        model_schema=omle.ModelSchema(
            features=[
                omle.Feature(name="sepal_length", source="X", index=0,
                                type=omle.TensorType(dtype=omle.DataType.FLOAT32, shape=[-1]),
                                measure_level=omle.MeasureLevel.CONTINUOUS),
                omle.Feature(name="sepal_width",  source="X", index=1,
                                type=omle.TensorType(dtype=omle.DataType.FLOAT32, shape=[-1]),
                                measure_level=omle.MeasureLevel.CONTINUOUS),
                omle.Feature(name="petal_length", source="X", index=2,
                                type=omle.TensorType(dtype=omle.DataType.FLOAT32, shape=[-1]),
                                measure_level=omle.MeasureLevel.CONTINUOUS),
                omle.Feature(name="petal_width",  source="X", index=3,
                                type=omle.TensorType(dtype=omle.DataType.FLOAT32, shape=[-1]),
                                measure_level=omle.MeasureLevel.CONTINUOUS),
            ],
            targets=[
                omle.Target(
                    name="species",
                    kind=omle.TargetKind.MULTICLASS,
                    class_labels=[omle.Scalar.string(s) for s in
                                  ("setosa", "versicolor", "virginica")],
                )
            ],
        ),
        tensor_entries=[
            omle.TensorEntry(id="coef", dense=omle.Tensor(
                name="coef",
                type=omle.TensorType(dtype=omle.DataType.FLOAT32, shape=[3, 4]),
                float32_data=[0.1]*12)),
            omle.TensorEntry(id="bias", dense=omle.Tensor(
                name="bias",
                type=omle.TensorType(dtype=omle.DataType.FLOAT32, shape=[3]),
                float32_data=[0.0, 0.0, 0.0])),
        ],
        nodes=[
            omle.Node(
                name="clf",
                domain="omle.ml",
                op="Linear",
                inputs=[omle.NodeInput(name="X")],
                outputs=[
                    omle.NodeOutput(name="y_pred", role=omle.OutputRole.PREDICTION),
                    omle.NodeOutput(name="y_prob", role=omle.OutputRole.PROBABILITY),
                ],
                linear=omle.Linear(
                    coefficients=omle.TensorRef(id="coef"),
                    intercept=omle.TensorRef(id="bias"),
                    post_transform=omle.PostTransform.SOFTMAX,
                ),
            )
        ],
        functions=[
            omle.DefineFunction(
                name="my_scale",
                parameters=[omle.FunctionParameter(name="x",
                             data_type=omle.DataType.FLOAT64)],
                result_data_type=omle.DataType.FLOAT64,
                body=omle.Expression(apply=omle.Apply(
                    function="mul",
                    arguments=[
                        omle.Expression.from_ref("x"),
                        omle.Expression.from_literal(omle.Scalar.float(2.0)),
                    ],
                )),
            )
        ],
    )
    path = tmp_path / "model.json"
    omle.save_json(model, path)
    return path


@pytest.fixture()
def invalid_model_file(tmp_path):
    """Write an invalid model JSON (missing format_version, bad output ref)."""
    import omle
    model = omle.OMLEModel(
        metadata=omle.ModelMetadata(format_version="", name="bad"),
        inputs=[omle.InputSpec(name="X")],
        outputs=[omle.OutputSpec(name="does_not_exist")],
    )
    path = tmp_path / "bad_model.json"
    # Bypass assert_valid to write the invalid file
    omle.save_json(model, path)
    return path


# ── Parser ────────────────────────────────────────────────────────────────────

def test_parser_validate_defaults():
    parser = _build_parser()
    args = parser.parse_args(["validate", "model.json"])
    assert args.command == "validate"
    assert args.file == "model.json"
    assert args.no_registry is False


def test_parser_validate_no_registry():
    parser = _build_parser()
    args = parser.parse_args(["validate", "model.json", "--no-registry"])
    assert args.no_registry is True


def test_parser_inspect_defaults():
    parser = _build_parser()
    args = parser.parse_args(["inspect", "model.json"])
    assert args.command == "inspect"
    assert args.section == "all"
    assert args.json is False
    assert args.verbose is False


def test_parser_inspect_section():
    parser = _build_parser()
    for section in ("metadata", "imports", "inputs", "outputs",
                    "schema", "nodes", "tensor_entries", "functions", "all"):
        args = parser.parse_args(["inspect", "model.json", "--section", section])
        assert args.section == section


def test_parser_inspect_invalid_section():
    parser = _build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["inspect", "model.json", "--section", "bogus"])


# ── validate command ──────────────────────────────────────────────────────────

def test_validate_valid_model(valid_model_file, capsys):
    with pytest.raises(SystemExit) as exc:
        main(["validate", str(valid_model_file)])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "valid" in out.lower()


def test_validate_invalid_model(invalid_model_file, capsys):
    with pytest.raises(SystemExit) as exc:
        main(["validate", str(invalid_model_file)])
    assert exc.value.code == 1
    out = capsys.readouterr().out
    assert "error" in out.lower() or "✗" in out


def test_validate_no_registry(valid_model_file, capsys):
    with pytest.raises(SystemExit) as exc:
        main(["validate", str(valid_model_file), "--no-registry"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "valid" in out.lower()


def test_validate_missing_file(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["validate", "/nonexistent/model.json"])
    assert exc.value.code == 2


def test_validate_exit_code_zero_on_valid(valid_model_file):
    with pytest.raises(SystemExit) as exc:
        main(["validate", str(valid_model_file)])
    assert exc.value.code == 0


def test_validate_exit_code_one_on_invalid(invalid_model_file):
    with pytest.raises(SystemExit) as exc:
        main(["validate", str(invalid_model_file)])
    assert exc.value.code == 1


# ── inspect command ───────────────────────────────────────────────────────────

def test_inspect_all_sections(valid_model_file, capsys):
    with pytest.raises(SystemExit) as exc:
        main(["inspect", str(valid_model_file)])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    for keyword in ("Metadata", "Inputs", "Outputs", "Schema", "Nodes", "Tensor entries"):
        assert keyword in out, f"Expected {keyword!r} in output"


def test_inspect_metadata_section(valid_model_file, capsys):
    with pytest.raises(SystemExit) as exc:
        main(["inspect", str(valid_model_file), "--section", "metadata"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "iris_clf" in out
    assert "scikit-learn" in out


def test_inspect_imports_section(valid_model_file, capsys):
    with pytest.raises(SystemExit) as exc:
        main(["inspect", str(valid_model_file), "--section", "imports"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "omle.ml" in out
    assert "omle.functions" in out


def test_inspect_inputs_section(valid_model_file, capsys):
    with pytest.raises(SystemExit) as exc:
        main(["inspect", str(valid_model_file), "--section", "inputs"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "X" in out
    assert "FLOAT32" in out


def test_inspect_outputs_section(valid_model_file, capsys):
    with pytest.raises(SystemExit) as exc:
        main(["inspect", str(valid_model_file), "--section", "outputs"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "y_pred" in out
    assert "PREDICTION" in out
    assert "y_prob" in out
    assert "PROBABILITY" in out


def test_inspect_schema_section(valid_model_file, capsys):
    with pytest.raises(SystemExit) as exc:
        main(["inspect", str(valid_model_file), "--section", "schema"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "sepal_length" in out
    assert "species" in out
    assert "MULTICLASS" in out
    assert "setosa" in out


def test_inspect_nodes_section(valid_model_file, capsys):
    with pytest.raises(SystemExit) as exc:
        main(["inspect", str(valid_model_file), "--section", "nodes"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "clf" in out
    assert "Linear" in out
    assert "coef" in out


def test_inspect_nodes_verbose(valid_model_file, capsys):
    with pytest.raises(SystemExit) as exc:
        main(["inspect", str(valid_model_file), "--section", "nodes", "--verbose"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "clf" in out


def test_inspect_constants_section(valid_model_file, capsys):
    with pytest.raises(SystemExit) as exc:
        main(["inspect", str(valid_model_file), "--section", "tensor_entries"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "coef" in out
    assert "bias" in out
    assert "FLOAT32" in out


def test_inspect_functions_section(valid_model_file, capsys):
    with pytest.raises(SystemExit) as exc:
        main(["inspect", str(valid_model_file), "--section", "functions"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "my_scale" in out
    assert "FLOAT64" in out


def test_inspect_json_output(valid_model_file, capsys):
    with pytest.raises(SystemExit) as exc:
        main(["inspect", str(valid_model_file), "--json"])
    assert exc.value.code == 0
    raw = capsys.readouterr().out
    d = json.loads(raw)
    assert d["metadata"]["name"] == "iris_clf"
    assert "inputs" in d
    assert "nodes" in d


def test_inspect_missing_file(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["inspect", "/nonexistent/model.json"])
    assert exc.value.code == 2


# ── predict ───────────────────────────────────────────────────────────────────
# `predict` forwards to the omle-predict binary that omle-runtime installs, in
# the same shape as `convert`. The binary is not a dependency of this package,
# so the tests cover the dispatch: the not-installed path, and that arguments
# and exit status are handed through untouched.

def test_predict_without_runtime_installed(monkeypatch, capsys):
    monkeypatch.setattr("shutil.which", lambda _name: None)
    with pytest.raises(SystemExit) as exc:
        main(["predict", "model.omle"])
    assert exc.value.code == 2
    assert "pip install omle-runtime" in capsys.readouterr().err


def test_predict_forwards_args_and_exit_code(monkeypatch):
    seen = {}

    def fake_call(cmd):
        seen["cmd"] = cmd
        return 3

    monkeypatch.setattr("shutil.which", lambda _name: "/usr/local/bin/omle-predict")
    monkeypatch.setattr("subprocess.call", fake_call)

    with pytest.raises(SystemExit) as exc:
        main(["predict", "model.omle", "in.csv", "out.csv"])

    assert exc.value.code == 3
    assert seen["cmd"] == [
        "/usr/local/bin/omle-predict", "model.omle", "in.csv", "out.csv",
    ]


def test_predict_forwards_help_rather_than_intercepting_it(monkeypatch):
    # -h belongs to omle-predict, not to this parser; the subcommand is
    # registered with add_help=False so it never gets swallowed here.
    seen = {}

    def fake_call(cmd):
        seen["cmd"] = cmd
        return 0

    monkeypatch.setattr("shutil.which", lambda _name: "omle-predict")
    monkeypatch.setattr("subprocess.call", fake_call)

    with pytest.raises(SystemExit):
        main(["predict", "-h"])

    assert seen["cmd"] == ["omle-predict", "-h"]


def test_predict_is_listed_in_help(capsys):
    parser = _build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--help"])
    assert "predict" in capsys.readouterr().out
