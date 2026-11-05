# OMLE Documentation

This directory contains the technical documentation for **OMLE — Open Machine Learning Exchange**.

## Design Overview

OMLE uses a hybrid representation designed to preserve machine learning semantics while supporting general inference pipelines.

An OMLE model combines:

```text
Model Schema
    │
    ▼
Operator Graph
    │
    ├── Preprocessing
    ├── Feature transformations
    ├── Structured ML models
    ├── Generic operators
    └── Postprocessing
```

### Model Schema

`ModelSchema`, `Feature`, and `Target` describe the logical model interface, including data types, measure levels, value domains, and preprocessing policies.

This allows OMLE models to preserve information beyond raw tensor shapes.

### Operator Graph

Inference is represented as a directed acyclic graph of named nodes.

Nodes consume named inputs and produce named outputs, allowing complete inference pipelines to include preprocessing, model execution, composition, and postprocessing.

Named graph values use the leading dimension:

```text
[N, ...]
```

where `N` is the batch size.

### Structured Models

Classical ML models can use dedicated structured representations rather than being reduced entirely to low-level arithmetic operators.

Examples include:

- trees and tree ensembles
- linear models
- SVM
- neural networks
- naive Bayes
- clustering
- KNN
- anomaly detection

This preserves model semantics and makes models easier to inspect, validate, convert, visualize, and optimize.

### Expressions and Generic Operators

OMLE uses two complementary mechanisms for computation:

- **Expressions** for elementwise operations such as arithmetic, comparisons, strings, dates, null handling, and value mapping.
- **Operators** for structural transformations, feature preprocessing, model execution, aggregation, and graph composition.

### Composite Nodes

`CompositeNode` defines an isolated subgraph with explicit inputs and outputs.

Internal nodes do not automatically inherit values from the enclosing graph, providing predictable scope and reusable composition.

### Model Verification

OMLE models can carry verification cases containing sample inputs, expected outputs, and numerical tolerances.

Verification allows consumers to check that a model behaves consistently after conversion, serialization, transport, or execution by another runtime.

## Proto Schema

The protobuf schema ([`protobuf/omle.proto`](../protobuf/omle.proto)) defines the wire format. Key messages:

- `OMLEModel` — root document containing metadata, imports, interface, schema, graph, tensor entries, and functions
- `ModelSchema` / `Feature` / `Target` — logical schema with preprocessing policies
- `Node` / `NodeInput` / `NodeOutput` — graph structure with rich output metadata
- `CompositeNode` / `NameAlias` — scoped subgraphs with explicit name binding
- `Expression` / `Apply` — elementwise tensor expression DSL
- `Predicate` — boolean predicate trees for trees and predicates
- `Tree` / `TreeEnsemble` / `Linear` / `NaiveBayes` / `Clustering` / `SVM` / `NeuralNetwork` / `AnomalyDetection` — structured model bodies
- `Tensor` / `TensorRef` / `TensorType` / `SparseTensor` / `CSRMatrix` — tensor storage, references, and type contracts

The features deferred beyond the current version are listed in the "restrictions" comment block at the top of [`protobuf/omle.proto`](../protobuf/omle.proto), which is the authoritative list.

## Operator Registry

Each operator entry declares input kinds, output type/shape/measure-level derivation rules, required attributes, validation constraints, and converter notes.

The generated per-operator reference is linked below.

### ML Model Operators

Trained model families. Most carry a dedicated protobuf message that preserves the model's own semantics; the rest carry their parameters as typed attributes.

- [`omle.ml`](reference/operators/omle.ml.md) — trees, ensembles, linear, SVM, neural networks, naive Bayes, clustering, KNN, anomaly detection

### Feature and Graph Operators

Everything around the model: preprocessing before it, and aggregation, voting, and score selection after it.

- [`omle.core`](reference/operators/omle.core.md) — structural manipulation, expression evaluation, reductions, voting
- [`omle.feature`](reference/operators/omle.feature.md) — preprocessing transformers such as scalers, encoders, imputers, and decomposition
- [`omle.text`](reference/operators/omle.text.md) — text normalization, tokenization, vectorization, and embeddings

The registry is authored as one file per namespace under `registries/operators/namespaces/`, merged at build time into `omle/registry/operators.json` inside the installed package.

The same layout is used for functions.

## Function Registry

The elementwise primitives available inside `Expression`.

Each entry declares argument types, return type rules, null propagation semantics, and measure-level derivation.

- [`omle.functions`](reference/functions/omle.functions.md) — arithmetic, comparison, logical, math, conditional, null handling, string, date, type conversion, and value mapping

## Versioning

OMLE uses three independently versioned axes:

- **Format version** (`ModelMetadata.format_version`) — the wire format, currently `0.1.0`. It moves only when `omle.proto` changes.
- **Namespace versions** (`NamespaceImport.version`) — operator and function sets, currently `0.1`, one version per namespace. Adding an operator bumps its namespace and leaves the format version unchanged.
- **Producer version** (`ModelMetadata.producer_version`) — the release of the tool that produced the model and may move with every tool release.

Compatibility is determined by evidence before declaration.

A model containing verification cases records what its producer computed. A consumer that reproduces those outputs has demonstrated that it can read the model correctly and should not reject it solely because of the declared version.

When a model contains no verification cases, the declared version becomes the primary compatibility signal.

The normative rule is documented on `format_version` in [`protobuf/omle.proto`](../protobuf/omle.proto).

The format is currently pre-1.0 and stabilizing toward a v1 release. Minor releases may still contain breaking changes before v1.

## Documents in This Directory

Hand-written documentation:

- [Composite scoping](composite-scoping.md) — name visibility at `CompositeNode` boundaries
- [Validation rules](validation-rules.md) — requirements for a conforming validator

Generated documentation:

- [`reference/`](reference/README.md) — per-operator and per-function reference generated from `registries/`

Generated reference documentation should not be edited directly.

Run:

```bash
python tools/gen_docs.py
```

to regenerate it after registry changes.

`tools/check_docs_current.py` verifies that generated documentation remains synchronized with the registry definitions.