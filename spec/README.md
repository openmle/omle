# OMLE Specification

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

Each operator entry declares input kinds, output type/shape/measure-level derivation rules, required attributes, validation constraints, and converter notes. The generated per-operator reference is linked below.

### ML model operators

Trained model families. Most carry a dedicated protobuf message that preserves the model's own semantics; the rest carry their parameters as typed attributes.

- [`omle.ml`](../docs/operators/omle.ml.md) — trees, ensembles, linear, SVM, neural networks, naive Bayes, clustering, KNN, anomaly detection

### Feature and graph operators

Everything around the model: preprocessing before it, and aggregation, voting and score selection after it.

- [`omle.core`](../docs/operators/omle.core.md) — structural manipulation, expression evaluation, reductions, voting
- [`omle.feature`](../docs/operators/omle.feature.md) — preprocessing transformers (scalers, encoders, imputers, decomposition)
- [`omle.text`](../docs/operators/omle.text.md) — text normalization, tokenization, vectorization, embeddings

The registry is authored as one file per namespace under `registries/operators/namespaces/`, merged at build time into `omle/registry/operators.json` inside the installed package. Same layout for functions.

## Function Registry

The elementwise primitives available inside `Expression`. Each entry declares argument types, return type rules, null propagation semantics, and measure level derivation.

- [`omle.functions`](../docs/functions/omle.functions.md) — arithmetic, comparison, logical, math, conditional, null handling, string, date, type conversion, value mapping

## Versioning

- **Format version** (`ModelMetadata.format_version`): semver string, currently `0.1.0`. Consumers reject incompatible MAJOR versions.
- **Namespace versions** (`NamespaceImport.version`): per-namespace versioning for operators and functions, currently `0.1`. New operators/functions can be added in MINOR bumps without breaking existing models.
- **Structured implementations**: versioned via the format version, not the namespace mechanism.

The format is pre-1.0 and stabilizing toward a v1 release; MINOR bumps may still include breaking changes until then.

## Documents in this directory

- [Composite scoping](composite-scoping.md) — name visibility at `CompositeNode` boundaries
- [Validation rules](validation-rules.md) — what a conforming validator must enforce
