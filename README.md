# OMLE

**Open Machine Learning Exchange** — an open, schema-aware interchange format for classical machine learning inference.

OMLE provides a compact binary format (protobuf) for representing trained ML models and their preprocessing and postprocessing pipelines. It preserves model semantics at a level practical for interoperability, conversion, validation, and deployment-oriented inference across major ML ecosystems.

## Why OMLE?

Classical ML has an interoperability gap:

- **PMML** is semantically rich but XML-based, verbose, and no meaningful updates for many years.
- **ONNX-ML** has poor support for classical ML semantics. It lacks schema-level concepts like feature binding, missing/invalid/outlier handling, measure levels, and value domains.
- **Framework-native formats** (pickle, joblib, XGBoost JSON, LightGBM text) are not portable and carry security risks.

OMLE fills this gap with a modern binary format that combines PMML's semantic richness with ONNX's operational pragmatism, under a permissive license.

| Capability | PMML | ONNX-ML | OMLE |
|---|---|---|---|
| Feature schema with measure levels | ✓ | ✗ | ✓ |
| Missing / invalid / outlier handling | ✓ | ✗ | ✓ |
| Structured ML models (trees, tree ensembles, linear, SVM, MLP, naive Bayes, clustering, anomaly detection) | ✓ | partial | ✓ |
| Generic ML models (KNN) | ✗ | ✗ | ✓ |
| Generic operator graph | ✗ | ✓ | ✓ |
| Embedded verification, warm-up and sample inputs | partial | ✗ | ✓ |
| Binary format | ✗ | ✓ | ✓ |
| Versioned operator registry | ✗ | ✓ | ✓ |
| Permissive license | ✓ | ✓ | ✓ |

## Design

OMLE uses a hybrid representation:

- **Logical schema** — named features and targets with types, measure levels, value domains, and preprocessing policies (missing, invalid, outlier handling)
- **Graph nodes** — a DAG of named operators spanning preprocessing, model scoring, and postprocessing
- **Structured model bodies** — dedicated proto messages for classical ML families where preserving high-level semantics matters

### Data Model

Every named value in the graph has shape `[N, ...]`, where `N` is the leading row dimension. The graph operates on a namespace of named tensors — nodes consume named values and produce new named values. Structured implementations use positional indexing into a flat slot space derived from their input list.

### Expression DSL

OMLE includes an elementwise expression sub-DSL for per-column derived computations. Expressions operate on `[N]` columns using a versioned set of 61 primitives (arithmetic, comparison, logical, math, conditional, null handling, string, date, type conversion, value mapping). The expression language is separate from the graph operator set — graph nodes handle structurally interesting operations, expressions handle elementwise math.

### Scope Isolation

`CompositeNode` introduces local namespaces for subgraph isolation. Internal nodes only see names explicitly passed as inputs — no transitive visibility into enclosing scopes. This enables clean composition of preprocessing pipelines and multi-model architectures without name collisions.

## Installation

The `omle` Python package is the reference implementation: the in-memory IR, protobuf serialization, validation, and the `omle` CLI.

```bash
# Core SDK (IR types, protobuf I/O, validation, CLI)
pip install omle

# With individual components
pip install "omle[convert]"   # converters (scikit-learn, Spark ML, XGBoost, LightGBM, CatBoost)
pip install "omle[runtime]"   # C++ inference runtime
pip install "omle[viewer]"    # Jupyter / browser DAG viewer

# Everything
pip install "omle[all]"
```

Requires Python 3.10+. `protobuf` is the only required dependency.

## Quick Start

```python
import omle

# Load a model — format is inferred from the extension
# (.omle / .pb / .bin → protobuf, .json → JSON)
model = omle.load("model.omle")

# Validate against structural rules and the operator/function registries
result = omle.validate(model)
if not result.is_valid:
    print(result)

# Inspect
print(model.metadata.format_version)
for fw in model.metadata.source_frameworks:
    print(fw.name, fw.version, fw.role)
for node in model.nodes:
    print(node.name, f"{node.domain}.{node.op}")

# Round-trip to JSON for diffing or hand-editing
omle.save(model, "model.json")
```

Converting a trained model requires `omle-convert`:

```python
from omle import export_omle

# scikit-learn, XGBoost, LightGBM, CatBoost — pass the fitted model
export_omle(sklearn_pipeline, "model.omle", X=X_test)

# Spark ML — pass a fitted PipelineModel; dataset supplies verification and sample rows
export_omle(pipeline_model, "spark_model.omle", dataset=train_df)
```

## Command-Line Interface

The `omle` CLI provides tools for working with model files:

```bash
# Validate a model file
omle validate model.omle
omle validate model.omle --no-registry

# Inspect a model's structure
omle inspect model.omle
omle inspect model.omle --section nodes
omle inspect model.omle --section metadata
omle inspect model.omle --json

# Open the interactive DAG viewer in a browser (requires omle-viewer)
omle view model.omle

# Convert a model to OMLE format (requires omle-convert).
# The source framework is auto-detected from the file contents or extension.
omle convert model.joblib    output.omle   # scikit-learn
omle convert saved_pipeline/ output.omle   # Spark ML
omle convert model.json      output.omle   # XGBoost JSON (or CatBoost JSON)
omle convert model.txt       output.omle   # LightGBM
omle convert model.cbm       output.omle   # CatBoost native
```

`omle convert` forwards all arguments to `omle-convert`; see its
[README](https://github.com/openmle/omle-convert) for the full option set.

## Reference

- **[Specification](https://github.com/openmle/omle/blob/main/spec/README.md)** — proto schema, registries, versioning
- **[Operator and function reference](https://github.com/openmle/omle/blob/main/docs/README.md)** — every ML model family, feature operator and expression primitive, generated from the registries

## Ecosystem

| Package                                                         | Language | Purpose |
|-----------------------------------------------------------------|---|---|
| [`omle`](https://github.com/openmle/omle)                 | Python | This package — IR, protobuf I/O, validation, CLI |
| [`omle-convert`](https://github.com/openmle/omle-convert) | Python | Converters from trained models to `.omle` |
| [`omle-runtime`](https://github.com/openmle/omle-runtime) | C++ (Python/Java bindings) | Inference runtime |
| [`omle-viewer`](https://github.com/openmle/omle-viewer)   | Python + TypeScript | Interactive DAG viewer for Jupyter and the browser |
| [`omle.js`](https://github.com/openmle/omle.js)           | TypeScript | Browser/Node loader, validator, and execution engine |

## Converter Status

Provided by [`omle-convert`](https://github.com/openmle/omle-convert):

| Framework | Status | Notes |
|---|---|---|
| Scikit-Learn | Available | Pipeline walker; trees, ensembles, linear, SVM, MLP, KNN, Naive Bayes, clustering, anomaly detection, decomposition, text, preprocessing; `category_encoders` supported |
| Spark ML | Available | Live (PySpark) and no-Spark (saved-format reader via pyarrow) paths; XGBoost4J and SynapseML LightGBM models |
| XGBoost | Available | Sklearn wrappers, native `Booster`, and `.json` files |
| LightGBM | Available | Sklearn wrappers, native `Booster`, and `.txt` files |
| CatBoost | Available | Sklearn wrappers and `.cbm` / `.json` files |
| PMML | Planned | Round-trip fidelity for the compliance audience |

## Contributing

OMLE is in active development. The proto schema and registries are stabilizing toward a v1 release. See [CONTRIBUTING.md](https://github.com/openmle/omle/blob/main/CONTRIBUTING.md) for development setup and the checks a change needs to pass, and [CODE_OF_CONDUCT.md](https://github.com/openmle/omle/blob/main/CODE_OF_CONDUCT.md) for community expectations.

Contributions are welcome in:

- Converter implementations
- Runtime implementations
- Validation tooling
- Documentation and specification refinements

## License

[Apache License v2.0](https://github.com/openmle/omle/blob/main/LICENSE)
