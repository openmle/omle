# OMLE Documentation

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

- [`omle.ml`](reference/operators/omle.ml.md) — trees, ensembles, linear, SVM, neural networks, naive Bayes, clustering, KNN, anomaly detection

### Feature and graph operators

Everything around the model: preprocessing before it, and aggregation, voting and score selection after it.

- [`omle.core`](reference/operators/omle.core.md) — structural manipulation, expression evaluation, reductions, voting
- [`omle.feature`](reference/operators/omle.feature.md) — preprocessing transformers (scalers, encoders, imputers, decomposition)
- [`omle.text`](reference/operators/omle.text.md) — text normalization, tokenization, vectorization, embeddings

The registry is authored as one file per namespace under `registries/operators/namespaces/`, merged at build time into `omle/registry/operators.json` inside the installed package. Same layout for functions.

## Function Registry

The elementwise primitives available inside `Expression`. Each entry declares argument types, return type rules, null propagation semantics, and measure level derivation.

- [`omle.functions`](reference/functions/omle.functions.md) — arithmetic, comparison, logical, math, conditional, null handling, string, date, type conversion, value mapping

## Versioning

Three axes, versioned independently:

- **Format version** (`ModelMetadata.format_version`) — the wire format, currently `0.1.0`. It moves only when `omle.proto` changes.
- **Namespace versions** (`NamespaceImport.version`) — operator and function sets, currently `0.1`, one version per namespace. Adding an operator bumps its namespace and leaves the format version alone.
- **Producer version** (`ModelMetadata.producer_version`) — the release of the tool that wrote the model, which moves on every release of that tool.

Compatibility is decided by evidence before declaration. A model carrying verification cases states what its producer computed; a consumer that reproduces those outputs has demonstrated it reads the model correctly, and must not then refuse it over its declared version. Only when a model carries no verification cases does the version become the sole evidence, and a consumer that does not implement it must say so rather than proceed silently. The normative rule is the comment on `format_version` in [`protobuf/omle.proto`](../protobuf/omle.proto).

The format is pre-1.0 and stabilizing toward a v1 release; MINOR bumps may still include breaking changes until then, which is why a pre-1.0 consumer treats an exact MINOR match as the bar.

## Documents in this directory

Hand-written, and the place to edit:

- [Composite scoping](composite-scoping.md) — name visibility at `CompositeNode` boundaries
- [Validation rules](validation-rules.md) — what a conforming validator must enforce

Generated, and not the place to edit:

- [`reference/`](reference/README.md) — the per-operator and per-function reference, produced from `registries/` by `python tools/gen_docs.py`. Edit the registry files; `tools/check_docs_current.py` fails the build when the two disagree.
