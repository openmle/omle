# OMLE — Open Machine Learning Exchange

[![PyPI](https://img.shields.io/pypi/v/omle.svg)](https://pypi.org/project/omle/)
[![Tests](https://github.com/openmle/omle/actions/workflows/test.yml/badge.svg)](https://github.com/openmle/omle/actions/workflows/test.yml)

**Portable machine learning models and pipelines across frameworks and runtimes.**

**Train anywhere. Run anywhere. Keep the model semantics.**

OMLE is an open, schema-aware interchange format for machine learning models and inference pipelines.

OMLE provides a compact Protocol Buffers representation for trained ML models together with their preprocessing and postprocessing pipelines. It is designed for interoperability, conversion, validation, and deployment-oriented inference across frameworks and runtimes.

```text
scikit-learn ─┐                         ┌─► Python
Spark ML ─────┤                         ├─► C/C++
XGBoost ──────┤                         ├─► Java/Scala
LightGBM ─────┼──► OMLE (.omle) ────────┼─► Spark
CatBoost ─────┤                         ├─► JavaScript
... ──────────┘                         ├─► REST / gRPC
                                        └─► ...
```

## Why OMLE?

Machine learning models are often trained in one environment but deployed in another.

Framework-native formats are convenient inside their own ecosystems, but are not designed as general cross-framework, cross-language interchange formats.

OMLE provides:

- **Portable model representation** independent of the original training framework
- **Complete inference pipelines** including preprocessing, model scoring, and postprocessing
- **Structured classical ML semantics** for trees, ensembles, linear models, SVM, clustering, and more
- **Explicit feature and target schemas**
- **Compact Protocol Buffers serialization**
- **Embedded verification, warm-up, and sample data**
- **Versioned operators and functions**
- **Cross-language inference**

OMLE uses a hybrid representation combining a logical schema, an operator graph, and structured model definitions where preserving ML semantics matters.

For the detailed design, see the [OMLE documentation](docs/README.md).

## Installation

The `omle` Python package provides the reference implementation: the in-memory IR, protobuf serialization, validation, and CLI.

```bash
# Core SDK
pip install omle

# Optional components
pip install "omle[convert]"   # converters
pip install "omle[runtime]"   # native C++ inference runtime
pip install "omle[server]"    # REST + gRPC inference server
pip install "omle[spark]"     # Spark ML integration
pip install "omle[viewer]"    # interactive model viewer

# Everything except the server
pip install "omle[all]"
```

Requires **Python 3.10+**. `protobuf` is the only required dependency of the core SDK.

## Quick Start

For complete workflows covering training, export, interactive visualization, and comparison of native and OMLE predictions, see the [`omle-models`](https://github.com/openmle/omle-models) notebooks.

### Convert a trained model

Model conversion is provided by [`omle-convert`](https://github.com/openmle/omle-convert).

```python
from omle import export_omle

# scikit-learn, XGBoost, LightGBM, CatBoost
export_omle(
    sklearn_pipeline,
    "model.omle",
    X=X_test,
)
```

Spark ML pipelines are supported as well:

```python
export_omle(
    pipeline_model,
    "spark_model.omle",
    dataset=train_df,
)
```

OMLE converts supported **complete pipelines**, including preprocessing stages, rather than only the final estimator.

To create an in-memory OMLE model:

```python
from omle import to_omle

model = to_omle(sklearn_pipeline, X=X_test)
```

### Load, validate, and run inference

```python
import omle

model = omle.load("model.omle")

result = omle.validate(model)
if not result.is_valid:
    print(result)

predictions = model.predict(X_test)
```

For classification models:

```python
probabilities = model.predict_proba(X_test)
```

For repeated inference:

```python
runtime = model.to_runtime(n_threads=4)
predictions = runtime.predict(X_test)
```

The native runtime is immutable and thread-safe.

For model inspection, JSON serialization, validation details, and runtime configuration, see the [documentation](docs/README.md).

## Command-Line Interface

The `omle` CLI provides common tools for working with OMLE models.

```bash
# Validate
omle validate model.omle

# Inspect
omle inspect model.omle
omle inspect model.omle --section nodes
omle inspect model.omle --section metadata
omle inspect model.omle --json

# Convert
omle convert model.joblib    output.omle   # scikit-learn
omle convert saved_pipeline/ output.omle   # Spark ML
omle convert model.json      output.omle   # XGBoost / CatBoost JSON
omle convert model.txt       output.omle   # LightGBM
omle convert model.cbm       output.omle   # CatBoost

# Predict
omle predict model.omle features.csv predictions.csv

# Open the model viewer
omle view model.omle
```

`omle convert` and `omle predict` delegate to the converter and runtime packages respectively. See the [`omle-convert`](https://github.com/openmle/omle-convert) and [`omle-runtime`](https://github.com/openmle/omle-runtime) READMEs for their full option sets.

## Supported Frameworks

Model conversion is provided by [`omle-convert`](https://github.com/openmle/omle-convert).

| Framework | Status | Notes |
|---|---|---|
| scikit-learn | Available | Pipelines, trees, ensembles, linear models, SVM, MLP, KNN, Naive Bayes, clustering, anomaly detection, decomposition, text, preprocessing, `category_encoders` |
| Spark ML | Available | Fitted pipelines, native Spark ML operators, XGBoost4J, SynapseML LightGBM |
| XGBoost | Available | scikit-learn wrappers, native `Booster`, JSON models |
| LightGBM | Available | scikit-learn wrappers, native `Booster`, text models |
| CatBoost | Available | scikit-learn wrappers, native models, CBM and JSON |
| PMML | Planned | Interoperability and compatibility use cases |
| ... | Planned | Additional frameworks and model ecosystems |

Support continues to expand as OMLE evolves toward v1.

## OMLE Ecosystem

OMLE is developed as a set of focused open-source projects.

| Project | Language | Purpose |
|---|---|---|
| [`omle`](https://github.com/openmle/omle) | Python / Protobuf | Specification, IR, serialization, validation, CLI |
| [`omle-convert`](https://github.com/openmle/omle-convert) | Python | Convert trained models and pipelines to OMLE |
| [`omle-runtime`](https://github.com/openmle/omle-runtime) | C++ / Python / Java | High-performance inference runtime |
| [`omle-server`](https://github.com/openmle/omle-server) | C++ / Python | REST and gRPC inference server |
| [`omle-spark`](https://github.com/openmle/omle-spark) | Scala / Python | Native OMLE scoring for Spark DataFrames |
| [`omle.js`](https://github.com/openmle/omle.js) | TypeScript | Browser and Node.js loader, validator, and runtime |
| [`omle-viewer`](https://github.com/openmle/omle-viewer) | TypeScript / Python | Interactive model visualization and debugging |

All projects are hosted under the [OpenMLE GitHub organization](https://github.com/openmle).

## Model Viewer

OMLE models can be inspected visually using the interactive DAG viewer.

Launch it locally:

```bash
omle view model.omle
```

Or use the hosted viewer directly in your browser: **[Open the viewer →](https://openmle.github.io/playground/viewer.html)**

The viewer runs entirely in the browser, so model files are not uploaded to a server. See [`omle-viewer`](https://github.com/openmle/omle-viewer) for details.

## OMLE, PMML, and ONNX

OMLE does not attempt to replace every model format. Different formats have different design centers.

- **Framework-native formats** are convenient when training and inference stay inside the same ecosystem.
- **PMML** provides rich semantic representations for classical ML and established many important concepts around schemas, preprocessing, model semantics, and verification.
- **ONNX** provides a general operator graph and is widely used for neural-network portability.
- **OMLE** focuses on portable classical ML inference, tabular pipelines, structured model semantics, explicit schemas, and deployment-oriented interoperability.

| Capability | PMML | ONNX / ONNX-ML | OMLE |
|---|:---:|:---:|:---:|
| Explicit feature schema | ✓ | Limited | ✓ |
| Missing / invalid / outlier policies | ✓ | Limited | ✓ |
| Structured classical ML models | ✓ | Partial | ✓ |
| Generic operator graph | Limited | ✓ | ✓ |
| Complete preprocessing pipelines | ✓ | ✓ | ✓ |
| Embedded verification data | Partial | Limited | ✓ |
| Compact binary representation | ✗ | ✓ | ✓ |
| Versioned operator/function registries | ✗ | ✓ | ✓ |

For the detailed OMLE design and specification, see [`docs/`](docs/README.md).

## Documentation

Technical documentation is available under [`docs/`](docs/README.md), including:

- protobuf schema
- logical model schema
- graph semantics
- structured models
- operators and functions
- expression DSL
- composite scoping
- model verification
- validation
- versioning

The generated [operator and function reference](docs/reference/README.md) is derived directly from the versioned registries.

## Project Status

OMLE is under active development.

The protobuf schema, registries, converters, and runtimes are being stabilized toward the first **OMLE v1** release.

Before v1, backwards-incompatible changes may still occur when they materially improve the specification.

## Contributing

Contributions and feedback are welcome.

Areas where contributions are especially useful include:

- converter implementations
- runtime implementations
- additional model and preprocessing support
- validation and verification tooling
- documentation and specification improvements
- interoperability and real-world deployment use cases

If OMLE does not yet support a framework, model type, or deployment environment you use, please open an issue and tell us about your use case.

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and contribution guidelines.

Community participation follows [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

OMLE is licensed under the [Apache License 2.0](LICENSE).

---

**Train anywhere. Run anywhere. Keep the model semantics.**
