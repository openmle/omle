# OMLE Registry Reference

_Registry version 0.1_

## ML Model Operators

Trained model families. Operators of kind `structured` carry a dedicated
protobuf message that preserves the model's own semantics; generic ones
carry their parameters as typed attributes.

- [`omle.ml`](operators/omle.ml.md) — ML model operators for OMLE v0.1. (9 operators, 8 with a dedicated proto body)

## Feature and Graph Operators

Everything around the model: preprocessing before it, and aggregation,
voting and score selection after it.

- [`omle.core`](operators/omle.core.md) — Core graph operators for OMLE v0.1. (26 operators, 1 with a dedicated proto body)
- [`omle.feature`](operators/omle.feature.md) — Feature preprocessing operators for OMLE v0.1. (31 operators)
- [`omle.text`](operators/omle.text.md) — Text preprocessing, tokenization, vectorization, and embedding operators for OMLE v0.1. (13 operators)

## Function Namespaces

- [`omle.functions`](functions/omle.functions.md) — Standard elementwise expression functions for OMLE v0.1. (61 functions)
