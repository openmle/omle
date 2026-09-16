# OMLE v0.1 Validation Rules

A consolidated list of rules a conforming OMLE validator must enforce. Rules are grouped by area. Severity is either **error** (validator must reject the model) or **warning** (validator must report but may accept).

---

## 1. Format and Version

**1.1** `ModelMetadata.format_version` must be a valid semver string in `MAJOR.MINOR.PATCH` form. *Error.*

**1.2** Validators must reject models whose MAJOR version exceeds the version they support. *Error.*

**1.3** Within a supported MAJOR version, validators may accept newer MINOR or PATCH versions only if all unknown fields can be safely ignored. *Error if not.*

---

## 2. Namespace Imports

**2.1** Every operator namespace referenced by `Node.domain` must appear in `OMLEModel.operator_imports`. *Error.*

**2.2** Every function namespace referenced by `Apply.function` must appear in `OMLEModel.function_imports`, unless the function is defined in `OMLEModel.functions`. *Error.*

**2.3** Namespaces beginning with `omle.` must not be redefined by producers. *Error.*

**2.4** Each `NamespaceImport` must specify a non-empty `namespace` and `version`. *Error.*

---

## 3. External Interface

**3.1** Every `InputSpec.name` must be unique within `OMLEModel.inputs`. *Error.*

**3.2** Every `OutputSpec.name` must resolve to either an `InputSpec.name` or a `NodeOutput.name` visible in the top-level namespace. *Error.*

**3.3** `OutputSpec.type` must be compatible with the resolved source value's type (same dtype, compatible shape). *Error.*

**3.4** When `OutputSpec.role = PROBABILITY` and `OutputBinding.target_name` resolves to a Target with `class_labels`:

- If the output is a multi-column probability tensor, the size of the last dimension must equal the number of `class_labels`. *Error.*
- If the output is a single-column probability for one bound class, `OutputBinding.values` must contain exactly one Scalar matching one of the `class_labels`. *Error.*

**3.5** `OutputBinding.target_name`, when set, must resolve to a `Target.name` declared in `ModelSchema.targets`. *Error.*

---

## 4. Schema

**4.1** Every `Feature.name` (after `NameRange` expansion) must be unique within `ModelSchema.features`. *Error.*

**4.2** `Feature.source` must reference an existing `InputSpec.name`. *Error.*

**4.3** `Feature.index` must be within the bounds of the source input's last dimension. For ranges, all expanded indices must be in bounds. *Error.*

**4.4** `Feature.missing_replacement_value` must be coercible to `Feature.type.dtype` when `missing_value_policy = MISSING_AS_VALUE`. *Error.*

**4.5** `Feature.invalid_replacement_value` must be coercible to `Feature.type.dtype` when `invalid_value_policy = INVALID_AS_VALUE`. *Error.*

**4.6** Every `Target.name` must be unique within `ModelSchema.targets`. *Error.*

**4.7** For `Target.kind = BINARY`, `class_labels` must contain exactly 2 entries. *Error.*

**4.8** For `Target.kind = MULTICLASS`, `class_labels` must contain at least 2 entries. *Error.*

**4.9** For `Target.kind = REGRESSION`, `class_labels` should be empty. *Warning if not.*

---

## 5. Range Expansion (NameRange)

**5.1** `NameRange.end` must be greater than or equal to `NameRange.start`. *Error.*

**5.2** `NameRange.start` must be non-negative. *Error.*

**5.3** `NameRange.width` must be non-negative. *Error.*

**5.4** Expansion order is ascending in `i`, producing names `prefix + format(i)` for `i` in `[start, end)`. Validators and runtimes must agree on this order. *Error if violated.*

**5.5** When `width > 0`, names are zero-padded to that width as a minimum (not maximum). For example, `width = 3` and `i = 5` produces `"005"`, while `i = 1234` produces `"1234"`. *Error if violated.*

**5.6** Expanded names must not collide with other names in the same scope. *Error.*

---

## 6. Top-Level Graph Namespace

**6.1** All names in the top-level scope must be unique. This includes: every `InputSpec.name`, every `Feature.name` (after expansion), and every `NodeOutput.name` of top-level nodes (after expansion). *Error.*

**6.2** Every `Node.name` at the top level must be unique within the top-level scope. *Error.*

**6.3** Every `NameAlias.from_name` and `NameAlias.to_name` must be a non-empty string. *Error.*

---

## 7. Tensor Entries

**7.1** Every `TensorEntry` in `OMLEModel.tensor_entries` must have its `id` field set. *Error.*

**7.2** Every `TensorEntry.id` in `OMLEModel.tensor_entries` must be unique. *Error.*

**7.3** Every `TensorRef.id` referenced from any node must resolve to an existing `TensorEntry` in `OMLEModel.tensor_entries`. *Error.*

**7.4** When `Tensor.raw_data` and a typed data field are both populated, they must encode consistent values. *Error if inconsistent.*

**7.5** A `Tensor` should populate either `raw_data` or one typed data field, not both. *Warning if both are populated.*

---

## 8. Node Structure and Inputs

**8.1** Every `Node.name` must be unique within its containing scope. *Error.*

**8.2** Every name referenced in `Node.inputs` (after `NameRange` expansion) must resolve to a value in the current scope's namespace at the time the node executes. *Error.*

**8.3** Nodes must form an acyclic dependency graph within each scope, determined by `inputs`/`outputs` relationships. *Error if cyclic.*

**8.4** Nodes must be listed in topological order consistent with their dependencies. *Error if not.*

**8.5** Every `NodeOutput.name` must be unique within the current scope. *Error.*

**8.6** A node's body (oneof) may have at most one variant set. *Error if multiple.*

**8.7** When a node has a structured body (Tree, TreeEnsemble, Linear, NaiveBayes, Clustering, SVM, NeuralNetwork, AnomalyDetection), `Node.domain` must be `omle.ml`. *Error.*

**8.8** When a node has a `composite` body, `Node.domain` and `Node.op` are advisory labels. *No validation required.*

---

## 9. NodeOutput

**9.1** `NodeOutput.name` must not be empty. *Error.*

**9.2** When `NodeOutput.type` is set, it must be consistent with the operator's registered output-type derivation rule. *Error if contradiction.*

**9.3** When `NodeOutput.measure_level` is set, it must be consistent with the operator's registered rule. *Error if contradiction.*

**9.4** Within a single node, no two `NodeOutput` entries may have the same `(role, binding)` pair. Bindings are compared by all fields except the `attributes` map. *Error.*

**9.5** When two outputs share a role, at least one must have a `binding` that distinguishes them. An empty binding is treated as a single bindable identity — a node may have at most one output of a given role with no binding. *Error if collision.*

**9.6** When `NodeOutput.role = PROBABILITY` and `binding.target_name` is set, the same shape rules as 3.4 apply (multi-column matches class count; single-column has a bound class). *Error.*

---

## 10. Slot Expansion

**10.1** Each `Node.inputs` entry (after `NameRange` expansion) contributes a number of slots equal to the product of its trailing dimensions:

- `[N]` contributes 1 slot
- `[N, D]` contributes D slots
- `[N, D1, ..., Dk]` contributes D1 × ... × Dk slots

*Definition.*

**10.2** Slots are ordered by row-major traversal of the trailing dimensions. *Definition.*

**10.3** When a structured body uses positional indexing (e.g., `Tree.split_feature`, `Linear.coefficients` shape), every index must be within `[0, total_slots)`. *Error.*

**10.4** Tensor refs in structured bodies whose shapes depend on `num_features` (e.g., `Linear.coefficients`, `NaiveBayes.means`, `Clustering.centers`) must align with the total slot count of the containing `Node.inputs`. *Error.*

---

## 11. Composite Nodes

### Composite Structure

**11.1** The internal subgraph of a `CompositeNode` must be acyclic and its nodes must be listed in topological order. *Error.*

### Input Aliases

**11.2** Each `NameAlias.from_name` in `input_aliases` must appear in the enclosing `Node.inputs` (after expansion). *Error.*

**11.3** Each `NameAlias.to_name` in `input_aliases` must be unique within the composite's local namespace and must not collide with internal node outputs. *Error.*

**11.4** No two input aliases may share the same `from_name`. *Error.*

**11.5** No two input aliases may share the same `to_name`. *Error.*

### Namespace Visibility

**11.6** Inside a composite, internal nodes may reference only names in the local namespace: inherited inputs (renamed or not) and outputs of earlier internal nodes. *Error if external reference.*

**11.7** Internal node outputs must not collide with inherited input names. Shadowing of inherited inputs is not permitted. *Error.*

**11.8** `Node.name` values within a composite must be unique within that composite's scope. *Error.*

### Output Aliases

**11.9** Each `NameAlias.from_name` in `output_aliases` must reference a value present in the local namespace at composite completion. *Error.*

**11.10** Each `NameAlias.to_name` in `output_aliases` must appear in the enclosing `Node.outputs`. *Error.*

**11.11** No two output aliases may share the same `from_name`. *Error.*

**11.12** No two output aliases may share the same `to_name`. *Error.*

### Output Publication

**11.13** The effective set of published external names — combining both direct name matches and output aliases — must exactly equal the set of names in the enclosing `Node.outputs`. Every declared external output must be published exactly once. *Error.*

### Scope Independence

**11.14** Names in different scopes (top-level vs. composite, sibling composites, nested composites) may coincide without conflict. *Definition.*

### Lint Warnings

**11.15** A composite input declared in the enclosing `Node.inputs` but never referenced by any internal node. *Warning.*

**11.16** An internal output that is neither consumed by a later internal node nor published via output aliases (or direct name match). *Warning.*

---

## 12. Expressions

**12.1** Every `Expression.ref` (a `NameRef`) must resolve to a value in the current scope. The referenced value may be a column `[N]`, a matrix `[N, F]`, or a higher-rank tensor whose first dimension is `N`. When `NameRef.field` is set, it must name one field within a matrix-like value. *Error.*

**12.2** Every `Apply.function` name must resolve to a function in an imported function namespace or in `OMLEModel.functions`. *Error.*

**12.3** Each `Apply.arguments` element must be a valid Expression producing a column, matrix, or higher-rank tensor whose leading dimension is `N` (or a literal that broadcasts). All arguments must be compatible under row-aligned evaluation, and the result shape must be statically inferable. *Error.*

**12.4** Function argument types must satisfy the function registry's `kinds` declaration after type promotion. *Error.*

**12.5** Variadic argument counts must satisfy the function's variadic specification (e.g., `coalesce` requires at least 2 arguments). *Error.*

**12.6** `map_values` must have an even number of pair elements; optional parameters (`default_value`, `map_missing_to`) follow the pair list. *Error if odd pair count.*

**12.7** An expression result must preserve the leading batch dimension: it must be a column `[N]` or a tensor whose first dimension is `N`. Expressions must not perform reductions across rows, row filtering, joins, aggregation, or dynamic shape changes. *Error.*

---

## 13. User-Defined Functions

**13.1** Every `DefineFunction.name` must be unique within `OMLEModel.functions`. *Error.*

**13.2** A user-defined function name must not collide with any function in an imported function namespace. *Error.*

**13.3** All `DefineFunction.parameters[].name` values must be unique within the function. *Error.*

**13.4** The function body must be a valid Expression. *Error.*

**13.5** The function body may reference only its declared parameter names. References to outer graph or composite scope names are not permitted. *Error.*

**13.6** Parameter names shadow any same-named values from outer scopes within the function body. *Definition.*

**13.7** No user-defined function may call itself directly or transitively. The call graph formed by `Apply` references inside `DefineFunction` bodies must be acyclic. *Error.*

**13.8** The body's inferred return type and measure level must be consistent with `result_data_type` and `result_measure_level`. *Error if contradiction.*

---

## 14. Predicates

**14.1** Every `SimplePredicate.column` and `SimpleSetPredicate.column` reference must resolve to a value in the current scope with shape `[N]`. *Error.*

**14.2** `SimplePredicate.value` must be coercible to the column's dtype, except for `IS_MISSING` and `IS_NOT_MISSING` which ignore `value`. *Error.*

**14.3** All entries in `SimpleSetPredicate.values` must be coercible to the column's dtype. *Error.*

**14.4** `CompoundPredicate.predicates` must contain at least 2 child predicates for `AND`, `OR`, `XOR`. For `SURROGATE`, at least 1. *Error.*

---

## 15. Attributes

**15.1** Every required attribute declared by an operator's registry entry must be present on the corresponding Node. *Error.*

**15.2** Each attribute's value type must match the registry's declared type (`int`, `float`, `string`, `bool`, `ints`, `floats`, `strings`, `bools`, `tensor_ref`, `type`, `expression`, `predicate`, `scalar`). *Error.*

**15.3** Attribute values must satisfy the operator's `enum_values` constraint when present. *Error.*

**15.4** When an attribute references a `TensorRef`, the reference must resolve to a `TensorEntry` in `OMLEModel.tensor_entries`. *Error.*

**15.5** When an attribute contains an Expression, the expression must be valid in the node's input namespace. *Error.*

**15.6** Operator-specific validation rules from the operator registry must be enforced. Examples:

- `OneHotEncode`: K = len(categories)
- `Impute`: Exactly one of `fill_value` or `fill_tensor` must be provided
- `Split`: Number of `Node.outputs` must equal len(sections); sum of sections must equal the last dimension of input
- `Select`: All candidate inputs must have the same shape and dtype
- `MaxAbsScaler`: Scale tensor must align with the trailing feature dimension

*Error.*

---

## 16. Structured Implementations

### 16.1 Tree

**16.1.1** Array lengths for `node_kind`, `split_feature`, `split_threshold`, `split_op`, `category_set_offset`, `category_set_count`, `default_child`, `leaf_value` must equal `num_nodes` where the field is populated. *Error.*

**16.1.2** Every `split_feature` value must be within `[0, total_slots)` for branch nodes. *Error.*

**16.1.3** For branch nodes using `IN_SET` or `NOT_IN_SET`, `category_set_offset[i] + category_set_count[i]` must not exceed `len(category_set)`. *Error.*

**16.1.4** Every `children_index` value must be within `[0, num_nodes)`. *Error.*

**16.1.5** The tree structure must be acyclic when followed via `children_index`. *Error.*

**16.1.6** `default_child[i]`, when populated for branch nodes, must be within `[0, num_nodes)`. *Error.*

**16.1.7** Each `ComplexPredicate.node_index` must be within `[0, num_nodes)`. *Error.*

**16.1.8** A node covered by a `ComplexPredicate` should use the full predicate semantics; if compact split fields are also populated for that node, the complex predicate takes precedence. *Warning if both exist.*

**16.1.9** When `leaf_vector_size > 1`, `leaf_vector_index[i] + leaf_vector_size` must not exceed `len(leaf_vector)` for leaf nodes. *Error.*

### 16.2 TreeEnsemble

**16.2.1** All trees in the ensemble must be individually valid per 16.1. *Error.*

**16.2.2** When `tree_weights` is populated, its length must equal `len(trees)`. *Error.*

**16.2.3** When `tree_group` is populated, its length must equal `len(trees)`, and every value must reference a valid class index. *Error.*

**16.2.4** `aggregation` must be set (not `AGGREGATION_UNSPECIFIED`). *Error.*

**16.2.5** When `post_transform` is set (not `POST_TRANSFORM_UNSPECIFIED`), the transform must be compatible with the aggregation and output semantics (e.g., `SOFTMAX` requires multi-class output). *Error.*

### 16.3 Linear

**16.3.1** `coefficients` must be set. *Error.*

**16.3.2** `coefficients` shape must be `[total_slots]` for single-output or `[num_outputs, total_slots]` for multi-output models. *Error.*

**16.3.3** When `intercept` is set, its shape must be `[]` (scalar), `[1]`, or `[num_outputs]` matching coefficients. *Error.*

**16.3.4** When `post_transform` is set, the transform must be compatible with the output semantics. *Error.*

### 16.4 NaiveBayes

**16.4.1** Exactly one variant of `NaiveBayes.implementation` must be set. *Error.*

**16.4.2** `class_log_priors` must be set, with shape `[num_classes]`. *Error.*

**16.4.3** For `GaussianNaiveBayes`: `means` and `variances` shapes must both be `[num_classes, total_slots]`. *Error.*

**16.4.4** For `MultinomialNaiveBayes` and `BernoulliNaiveBayes`: `feature_log_prob` shape must be `[num_classes, total_slots]`. *Error.*

**16.4.5** For `CategoricalNaiveBayes`: `len(category_offset)` must equal `len(category_count)`. *Error.*

**16.4.6** For `CategoricalNaiveBayes`: the sum of `category_count` must equal the trailing dimension of `category_log_prob` divided by `num_classes`. *Error.*

### 16.5 Clustering

**16.5.1** Exactly one variant of `Clustering.implementation` must be set. *Error.*

**16.5.2** For `PrototypeClustering`: `centers` shape must be `[num_clusters, total_slots]`. *Error.*

**16.5.3** For `PrototypeClustering`: `distance_measure` must be set (not `DISTANCE_MEASURE_UNSPECIFIED`). *Error.*

**16.5.4** For `PrototypeClustering`: when `cluster_labels` is populated, its length must equal `num_clusters`. *Error.*

**16.5.5** For `GaussianMixtureClustering`: `weights` shape must be `[num_clusters]`. *Error.*

**16.5.6** For `GaussianMixtureClustering`: `means` shape must be `[num_clusters, total_slots]`. *Error.*

**16.5.7** For `GaussianMixtureClustering`: `covariance_type` must be set (not `COVARIANCE_TYPE_UNSPECIFIED`). *Error.*

**16.5.8** For `GaussianMixtureClustering`: `covariances` shape must match `covariance_type`:

- `FULL` → `[num_clusters, total_slots, total_slots]`
- `DIAGONAL` → `[num_clusters, total_slots]`
- `SPHERICAL` → `[num_clusters]`

*Error.*

**16.5.9** For `GaussianMixtureClustering`: when `component_labels` is populated, its length must equal `num_clusters`. *Error.*

---

## 17. Operator-Registry Rules

**17.1** Every operator referenced by `Node.op` and `Node.domain` must be defined in the corresponding namespace's operator registry at a version compatible with the imported namespace version. *Error.*

**17.2** The number of `Node.inputs` (after expansion) must satisfy the operator's input arity (fixed count or variadic minimum). *Error.*

**17.3** Each input's type and shape must match the operator's input `kinds` and `shape_constraints`. *Error.*

**17.4** All operator-specific `validation_rules` from the operator registry must be satisfied. *Error.*

**17.5** Output-type derivation rules must produce results consistent with declared `NodeOutput.type` when both are present. *Error if contradiction.*

---

## 18. Function-Registry Rules

**18.1** Every function referenced by `Apply.function` must be defined in an imported function namespace at a compatible version, or in `OMLEModel.functions`. *Error.*

**18.2** Function argument count and types must match the function's signature after applicable type promotion. *Error.*

**18.3** Variadic argument constraints (minimum count, optional parameters) must be satisfied. *Error.*

**18.4** Null propagation, type promotion, and measure level rules from the function registry are part of the semantic contract. Validators do not need to check runtime behavior, but converters must produce expressions consistent with these rules. *Definition.*

---

## 19. Cross-Cutting

**19.1** Every reference (input names, output names, target names, function names, namespace names, tensor ref names) must resolve before the model is accepted. *Error if dangling.*

**19.2** No two top-level entities (inputs, schema features, top-level node outputs) may share a name after `NameRange` expansion. *Error.*

**19.3** Validators must process the model recursively, applying scope-local rules at each composite level. *Definition.*

**19.4** Validators should produce diagnostic output identifying the offending field path, scope, and rule number when reporting errors or warnings. *Recommended.*

---

## Summary

**Errors** halt acceptance of the model: format or version mismatches, dangling references, scope violations, type or shape contradictions, structural impossibilities (cycles, missing required fields), and uniqueness violations.

**Warnings** are advisory and do not halt acceptance: dead code, unused inputs, missing but recoverable metadata, redundant data encodings, and style recommendations.

**Definitions** are not validation rules but semantic statements that other rules depend on. They establish the meaning of terms like slot expansion, scope independence, and null propagation.

A reference validator should expose a **strict mode** (errors only) and a **lint mode** (errors plus warnings), with structured diagnostics keyed to the rule numbers above for traceability.
