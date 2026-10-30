# Composite Node Scoping Rules

This document defines the precise semantic rules for how names are visible, resolved, extended, and published at `CompositeNode` boundaries in OMLE v0.1.

## Overview

A `CompositeNode` introduces a local namespace isolated from the enclosing graph. Internal nodes execute within this local namespace and cannot reference names outside it except through the composite's explicitly declared inputs. Values produced inside the composite are not visible to the enclosing graph except through the composite's explicitly declared outputs.

Composite scoping serves three purposes:

1. **Explicit dependency contracts.** By examining a composite's declared inputs and outputs, a reader, validator, or optimizer can determine exactly what values the composite consumes and produces, without inspecting its internal structure.

2. **Name isolation.** Two composites can independently produce values with identical internal names without conflict. A composite's internal naming decisions are insulated from the rest of the graph.

3. **Refactoring safety.** Moving a composite to a different position in the graph requires only that the new position provides the composite's declared inputs. There are no hidden dependencies on enclosing names.

## Namespace Structure

OMLE defines a hierarchy of namespaces, one per scope:

- The **top-level namespace** is the root scope. It is populated by `ModelSchema` preprocessing (from external `InputSpec` and `Feature` declarations) and extended by the outputs of top-level nodes.

- Each `CompositeNode` introduces a **local namespace**, distinct from the enclosing namespace. A local namespace is initialized from the composite's declared inputs and extended by the outputs of its internal nodes.

- Composites may contain other composites. Each nested composite has its own local namespace, initialized from the nested composite's declared inputs (drawn from the parent composite's local namespace) and extended by its internal node outputs.

Names in different namespaces are distinct values, even when they spell the same string. A value named `score` in one composite's local namespace and a value named `score` in another composite's local namespace are unrelated.

## Namespace Initialization

At the start of a composite's execution, its local namespace is initialized from the enclosing `Node.inputs`:

- For each `NameAlias` in `CompositeNode.input_aliases`, the value bound to `from_name` in the enclosing graph is placed in the local namespace under `to_name`.

- For each enclosing input not covered by an alias, the value is inherited under its external name directly.

No other names from the enclosing graph are placed into the local namespace. Names in the enclosing namespace that are not listed in the composite's `Node.inputs` are not visible to the composite's internal nodes, regardless of whether they exist at the time the composite executes.

## Namespace Extension

As internal nodes execute in topological order, each internal node extends the local namespace with its `NodeOutput` entries. For each `NodeOutput` declared on an internal node, the produced value is placed into the local namespace under the declared name.

Names in the local namespace must be unique. Specifically:

- An internal node's output name must not collide with any other internal node's output name within the same composite.
- An internal node's output name must not collide with any of the composite's inherited input names.

Producing a value with a name that already exists in the local namespace is a validation error. Shadowing of inherited inputs is not permitted.

## Name Visibility

Internal nodes of a composite may reference, in their `Node.inputs` list, only:

- Names inherited from the composite's input bindings.
- Names produced by an earlier internal node in the composite's `nodes` list.

Internal nodes may not reference any other names. In particular, internal nodes cannot reference:

- Names in the enclosing namespace that are not declared as composite inputs.
- Names in sibling composites (composites at the same level as the current composite in the enclosing namespace).
- Names in nested composites contained within the current composite.
- Names in any other composite anywhere in the graph.

A reference to a name that does not exist in the local namespace is a validation error.

## Output Publication

When the composite completes, values are published back to the enclosing graph under the names declared in the enclosing `Node.outputs`. Publication follows a two-tier resolution:

- For each `NameAlias` in `CompositeNode.output_aliases`, the local value named `from_name` is published to the enclosing graph under `to_name`.

- For each enclosing output not covered by an alias, the local value with the same name is published directly.

In both cases, the source local value must exist in the local namespace at composite completion. It is a validation error if neither an alias nor a matching local value can be found for a declared external output.

The effective set of published external names must exactly match the set of names declared in the enclosing `Node.outputs`. Every declared output must be published exactly once, and no alias may publish to a name not declared in the enclosing outputs.

Values in the local namespace that are not published to an enclosing output are discarded when the composite completes. They are not visible to the enclosing graph.

## Name Uniqueness

Name uniqueness is scope-local. The full uniqueness rule for OMLE is:

- Within any single namespace, all `NodeOutput.name` values must be unique. This applies to the top-level namespace and to every composite's local namespace independently.
- `Node.name` values must be unique within each scope. Two composites may each contain a node named `scaler` without conflict; one composite may not contain two nodes named `scaler`.
- Names in different namespaces may coincide without conflict.

## Nested Composites

Composites may contain other composites. A nested composite has its own local namespace scoped to the immediately enclosing composite, not to the top level. The visibility, extension, and publication rules apply recursively at each level.

There is no transitive visibility across scope boundaries. A deeply nested internal node cannot reach a top-level value except through explicit input declarations at every intermediate level.

## Input and Output Aliases

Both `input_aliases` and `output_aliases` are optional. When empty, all names inherit or publish by direct name match. Aliases are only needed when internal and external names differ.

**Input alias rules:**

- Each `NameAlias.from_name` must appear in the enclosing `Node.inputs`.
- Each `NameAlias.to_name` must be unique within the composite's local namespace and must not collide with internal node outputs.
- No two input aliases may share the same `from_name` or the same `to_name`.

**Output alias rules:**

- Each `NameAlias.from_name` must reference a value present in the local namespace at composite completion.
- Each `NameAlias.to_name` must appear in the enclosing `Node.outputs`.
- No two output aliases may share the same `from_name` or the same `to_name`.

## Validation Algorithm

A conforming validator processes the graph recursively, maintaining the active namespace at each point of traversal:

1. At the top level, collect all `InputSpec.name`, `Feature.name` (after `NameRange` expansion), and `NodeOutput.name` values from top-level nodes. Check that all names are unique within the top-level namespace.

2. For each top-level node, in topological order determined by input/output dependencies, verify that its `Node.inputs` references all resolve in the top-level namespace. Extend the namespace with the node's declared outputs.

3. When a top-level node has a `composite` body, descend into the composite:

    a. Initialize the composite's local namespace using `input_aliases` and the enclosing `Node.inputs`. Values for these names are inherited from the top-level namespace.

    b. For each internal node, in topological order, verify that its `Node.inputs` references are present in the local namespace. Extend the local namespace with the internal node's outputs. Check that output names do not collide with existing names in the local namespace.

    c. If an internal node is itself a composite, recurse with the current local namespace as its enclosing namespace.

    d. After all internal nodes have been processed, verify output publication: for each name in the enclosing `Node.outputs`, check that either an output alias publishes it or a local value with the matching name exists.

4. Reject any reference that does not resolve in its current scope.

## Lint Warnings

Validators should emit non-fatal warnings (not errors) for:

- **Unused declared inputs.** A composite input declared in the enclosing `Node.inputs` but never referenced by any internal node. These indicate unused dependencies that can be removed.

- **Dead internal outputs.** An internal output that is neither consumed by a later internal node nor published via output aliases. These indicate dead code that can be removed.

## Worked Example

Consider a top-level graph with a model schema defining five features: `amount`, `merchant`, `user_age`, and `user_tenure_days`. The model applies two preprocessing composites and a classifier.

### Model structure

```
ModelSchema:
  Feature: amount          (CONTINUOUS)
  Feature: merchant        (NOMINAL)
  Feature: user_age        (CONTINUOUS)
  Feature: user_tenure_days (CONTINUOUS)

Top-level nodes:
  preprocess_transaction  (composite)
  preprocess_user         (composite)
  classifier              (TreeEnsemble)
```

### Node definitions

```protobuf
Node {
  name: "preprocess_transaction"
  inputs: [{ name: "amount" }, { name: "merchant" }]
  outputs: [
    NodeOutput { name: "amount_scaled" }
    NodeOutput { name: "merchant_encoded" }
  ]
  body: {
    composite: {
      nodes: [
        Node {
          name: "scale_amount"
          op: "StandardScaler"
          inputs: [{ name: "amount" }]
          outputs: [NodeOutput { name: "amount_scaled" }]
        }
        Node {
          name: "encode_merchant"
          op: "OrdinalEncoder"
          inputs: [{ name: "merchant" }]
          outputs: [NodeOutput { name: "merchant_encoded" }]
        }
      ]
      // input_aliases and output_aliases both empty — direct name match
    }
  }
}

Node {
  name: "preprocess_user"
  inputs: [{ name: "user_age" }, { name: "user_tenure_days" }]
  outputs: [
    NodeOutput { name: "user_age_scaled" }
    NodeOutput { name: "user_tenure_scaled" }
  ]
  body: {
    composite: {
      nodes: [
        Node {
          name: "scale_age"
          op: "StandardScaler"
          inputs: [{ name: "user_age" }]
          outputs: [NodeOutput { name: "user_age_scaled" }]
        }
        Node {
          name: "scale_tenure"
          op: "StandardScaler"
          inputs: [{ name: "user_tenure_days" }]
          outputs: [NodeOutput { name: "user_tenure_scaled" }]
        }
      ]
    }
  }
}

Node {
  name: "classifier"
  inputs: [
    { name: "amount_scaled" }
    { name: "merchant_encoded" }
    { name: "user_age_scaled" }
    { name: "user_tenure_scaled" }
  ]
  outputs: [NodeOutput { name: "fraud_probability", role: PREDICTION }]
  body: { tree_ensemble: { ... } }
}
```

### Namespace trace

**Top-level namespace after schema preprocessing:**
```
{ amount, merchant, user_age, user_tenure_days }
```

**Processing `preprocess_transaction`:**

Initialize local namespace from declared inputs:
```
local = { amount, merchant }
```

Note: `user_age` and `user_tenure_days` are not declared as inputs to this composite and are therefore invisible to its internal nodes.

Execute `scale_amount`:
```
local = { amount, merchant, amount_scaled }
```

Execute `encode_merchant`:
```
local = { amount, merchant, amount_scaled, merchant_encoded }
```

Check output publication: `amount_scaled` and `merchant_encoded` are both present in the local namespace. Both match the enclosing `Node.outputs` by direct name. Publish them to the top-level namespace.

**Top-level namespace after `preprocess_transaction`:**
```
{ amount, merchant, user_age, user_tenure_days,
  amount_scaled, merchant_encoded }
```

**Processing `preprocess_user`:**

Initialize local namespace from declared inputs:
```
local = { user_age, user_tenure_days }
```

Note: this composite cannot see `amount_scaled` or `merchant_encoded` from the top-level namespace, because they are not in its declared inputs.

Execute `scale_age` and `scale_tenure`, producing `user_age_scaled` and `user_tenure_scaled`.

Publish to the top-level namespace.

**Top-level namespace after `preprocess_user`:**
```
{ amount, merchant, user_age, user_tenure_days,
  amount_scaled, merchant_encoded,
  user_age_scaled, user_tenure_scaled }
```

**Processing `classifier`:**

The classifier is a non-composite node. It executes in the top-level namespace directly. Its inputs (`amount_scaled`, `merchant_encoded`, `user_age_scaled`, `user_tenure_scaled`) all resolve in the top-level namespace. It produces `fraud_probability`.

**Final top-level namespace:**
```
{ amount, merchant, user_age, user_tenure_days,
  amount_scaled, merchant_encoded,
  user_age_scaled, user_tenure_scaled,
  fraud_probability }
```

### Key observations

- Inside `preprocess_transaction`, the value `user_age` is invisible. Internal nodes cannot reach it because it was not declared as an input to this composite.

- Both composites could independently produce a value named `temp` or `intermediate` internally without conflict, because each composite's local namespace is isolated.

- Both composites contain nodes named with the prefix `scale_` but use different suffixes. Even if both had an internal node named `scaler`, there would be no conflict, because node names are scope-local.

- The classifier node sees only published names from both composites plus the original schema features. It has no knowledge of or access to internal composite names like `scale_amount` or `encode_merchant`.

### Example with aliases

If the internal structure needed different names than the external contract, aliases provide the rebinding:

```protobuf
Node {
  name: "preprocess_transaction"
  inputs: [{ name: "amount" }, { name: "merchant" }]
  outputs: [
    NodeOutput { name: "tx_amount_norm" }
    NodeOutput { name: "tx_merchant_id" }
  ]
  body: {
    composite: {
      input_aliases: [
        // No input aliases needed — "amount" and "merchant" work as-is internally
      ]
      nodes: [
        Node {
          op: "StandardScaler"
          inputs: [{ name: "amount" }]
          outputs: [NodeOutput { name: "scaled" }]
        }
        Node {
          op: "OrdinalEncoder"
          inputs: [{ name: "merchant" }]
          outputs: [NodeOutput { name: "encoded" }]
        }
      ]
      output_aliases: [
        // Internal "scaled" published as external "tx_amount_norm"
        NameAlias { from_name: "scaled", to_name: "tx_amount_norm" }
        // Internal "encoded" published as external "tx_merchant_id"
        NameAlias { from_name: "encoded", to_name: "tx_merchant_id" }
      ]
    }
  }
}
```

Here the internal nodes use short generic names (`scaled`, `encoded`) while the enclosing graph sees descriptive external names (`tx_amount_norm`, `tx_merchant_id`). The output aliases bridge the gap. Without aliases, the internal nodes would need to produce values named `tx_amount_norm` and `tx_merchant_id` directly.

## Future Extensions

OMLE v0.1 composites are always defined inline at their use site. A future version may introduce the following backward-compatible extensions:

- **Reusable composite definitions.** A top-level `composite_definitions` field containing named, reusable composite bodies, referenced by name from multiple call sites. Input and output aliases become essential here because the same internal body needs to work with different external names at different call sites.

- **Composite definition library.** A registry of community-defined composite patterns (e.g., standard preprocessing pipelines, common feature engineering blocks) that converters can reference rather than inline.

In v0.1, these features are not present. Composites are inline, and name matching is direct by default with aliases available for renaming when needed.

## Summary of Rules

1. A composite's local namespace is initialized from the composite's declared `Node.inputs`. Inherited inputs retain their external names unless renamed by an input alias.

2. Internal nodes extend the local namespace with their outputs. Output names must be unique within the local namespace and must not shadow inherited inputs.

3. Internal nodes may reference only names in the local namespace. They cannot reference names in the enclosing namespace, sibling namespaces, or child namespaces.

4. When the composite completes, values are published to the enclosing graph under the enclosing `Node.outputs` names, using output aliases when provided and direct name match otherwise.

5. Unpublished local values are discarded when the composite completes.

6. Name uniqueness is scope-local: each namespace (top-level and each composite's local namespace) has its own independent uniqueness requirement.

7. Validators verify all of the above, and additionally warn about declared inputs that are unused and about internal outputs that are neither consumed nor published.
