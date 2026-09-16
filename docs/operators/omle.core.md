# omle.core — Operators

_Core graph operators for OMLE v0.1._

**Registry version:** 0.1

## Operators

| Operator | Category | Kind | Summary |
|----------|----------|------|---------|
| [`Identity`](#identity) | core | generic | Pass input through unchanged. |
| [`Composite`](#composite) | structural | structured | Structured subgraph node with local scope and published inputs and outputs. |
| [`Cast`](#cast) | core | generic | Cast a tensor to a target dtype. |
| [`Concat`](#concat) | core | generic | Concatenate inputs along the last dimension. |
| [`Split`](#split) | core | generic | Split a tensor along the last dimension into multiple outputs. |
| [`Reshape`](#reshape) | core | generic | Reshape a tensor while preserving the leading row dimension. |
| [`TakeSlots`](#takeslots) | core | generic | Select, reorder, and optionally duplicate slots from the expanded flat slot space of one or more inputs. |
| [`Derive`](#derive) | expression | generic | Produce derived column or tensor values from an embedded Expression. |
| [`Select`](#select) | core | generic | Select one of multiple candidate values using a row-wise selector. |
| [`Clip`](#clip) | core | generic | Clamp numeric values to a range. |
| [`SparseToDense`](#sparsetodense) | core | generic | Convert a sparse tensor to its dense tensor form. |
| [`DenseToSparse`](#densetosparse) | core | generic | Convert a dense tensor to its sparse tensor form. |
| [`ArgMax`](#argmax) | selection | generic | Return the index of the maximum value in each row of a numeric matrix. |
| [`SelectByPrimarySecondaryScore`](#selectbyprimarysecondaryscore) | selection | generic | Select one class index per row using primary scores first and secondary scores as tie-break. |
| [`Sum`](#sum) | reduction | generic | Elementwise sum of aligned tensors. |
| [`Average`](#average) | reduction | generic | Elementwise arithmetic mean of aligned tensors. |
| [`WeightedSum`](#weightedsum) | reduction | generic | Elementwise weighted sum of aligned tensors. |
| [`WeightedAverage`](#weightedaverage) | reduction | generic | Elementwise weighted average of aligned tensors. |
| [`WeightedMedian`](#weightedmedian) | reduction | generic | Elementwise weighted median across aligned numeric inputs. |
| [`Min`](#min) | reduction | generic | Elementwise minimum across aligned tensors. |
| [`Max`](#max) | reduction | generic | Elementwise maximum across aligned tensors. |
| [`Median`](#median) | reduction | generic | Elementwise median across aligned tensors. |
| [`MajorityVote`](#majorityvote) | voting | generic | Majority vote over aligned class-label columns. |
| [`WeightedMajorityVote`](#weightedmajorityvote) | voting | generic | Weighted majority vote over aligned class-label columns. |
| [`SAMMEVote`](#sammevote) | voting | generic | Aggregate classifier predictions using the SAMME multiclass AdaBoost voting rule. |
| [`SoftVote`](#softvote) | voting | generic | Average or row-normalize aligned probability tensors across models. |

---

## Identity

**Category:** core  ·  **Since:** 0.1  ·  **Kind:** generic

Pass input through unchanged.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `x` | yes | no | tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | same_type(x) | same_shape(x) | same_measure_level(x) |  |

### Attributes

_(none)_

### Converter Notes

- Equivalent source operators: identity/pass-through nodes in preprocessing pipelines; sklearn FunctionTransformer with func=None or identity-like functions; Spark SQLTransformer SELECT pass-through expressions; PMML identity DerivedField patterns.
- Coverage notes: Identity preserves dtype, shape, measure level, and values exactly. It is useful for explicit wiring, naming, or schema-preserving graph normalization.
- Lowering notes: Converters may emit Identity when a source step is semantically a no-op but an explicit node is helpful for preserving pipeline structure, output names, or debugging visibility.

---

## Composite

**Category:** structural  ·  **Since:** 0.1  ·  **Kind:** structured  ·  **Body type:** `composite`

Structured subgraph node with local scope and published inputs and outputs.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `xs` | no | yes | tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `ys` | derived_from_body | derived_from_body | derived_from_body |  |

### Attributes

_(none)_

### Validation Rules

- Executable content is defined by body.composite.
- Composite input resolution follows composite input alias and local scope rules.
- Composite output resolution follows composite output alias and published output rules.
- The number, type, shape, and measure level of outputs are derived from the composite body.

### Converter Notes

- Equivalent source operators: nested pipelines, column transformers, model chains, or reusable subgraphs from source frameworks when represented as an embedded OMLE subgraph.
- Coverage notes: Composite represents structured subgraph execution with local scope, explicit input resolution, and published outputs. It is not a primitive mathematical operation.
- Lowering notes: Converters should use Composite when preserving a nested source structure improves readability or when a source step naturally lowers to multiple OMLE nodes with local intermediate names.

---

## Cast

**Category:** core  ·  **Since:** 0.1  ·  **Kind:** generic

Cast a tensor to a target dtype.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `x` | yes | no | tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | same_type(attr:output_dtype) | same_shape(x) | same_measure_level(x) |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `output_dtype` | string | yes |  |  |

### Converter Notes

- Equivalent source operators: dtype conversion steps such as numpy astype, Spark SQL CAST expressions, PMML type conversions, and explicit framework converter casts.
- Coverage notes: Cast changes dtype while preserving shape and measure level. It does not imply semantic recoding, category lookup, scaling, or parsing of free-form strings beyond the declared dtype conversion semantics.
- Lowering notes: Converters should insert Cast when source framework behavior requires a concrete dtype for downstream operators or output compatibility. Avoid using Cast to encode categorical mapping; use feature encoders instead.

---

## Concat

**Category:** core  ·  **Since:** 0.1  ·  **Kind:** generic

Concatenate inputs along the last dimension.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `xs` | yes | yes | tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | same_type_as_all_inputs | concat_last_dim(inputs) | derived_from_input_and_operator |  |

### Attributes

_(none)_

### Validation Rules

- All inputs must have the same leading row dimension N.
- All inputs must be compatible on all dimensions except the last.
- All inputs must have the same dtype.

### Converter Notes

- Equivalent source operators: sklearn ColumnTransformer / FeatureUnion output concatenation; Spark VectorAssembler-style feature assembly; PMML field concatenation patterns after independent transformations.
- Coverage notes: Concat joins tensors along the last dimension and requires compatible leading dimensions and dtype. It is primarily used to assemble feature matrices or combine aligned model outputs.
- Lowering notes: Converters should use Concat to materialize an ordered feature vector from multiple columns or transformed blocks. If source inputs have mixed dtypes, insert explicit casts or encode columns before concatenation.

---

## Split

**Category:** core  ·  **Since:** 0.1  ·  **Kind:** generic

Split a tensor along the last dimension into multiple outputs.

Produces one output per entry in sections. The single variadic output template is instantiated once for each produced output, in order.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `x` | yes | no | tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | same_type(x) | split_last_dim(x,sections) | same_measure_level(x) |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `sections` | ints | yes |  |  |

### Validation Rules

- The number of Node.outputs must equal len(sections).
- Each section must be positive.
- The sum of sections must equal the last dimension of x.

### Converter Notes

- Equivalent source operators: fixed column slicing from assembled vectors, vector-to-columns expansion, and decomposition of multi-output tensors into named outputs.
- Coverage notes: Split partitions the last dimension according to fixed sections and produces one output per section. It is static and does not perform data-dependent splitting.
- Lowering notes: Converters may use Split to expose named outputs from a matrix or vector, or to reverse an earlier Concat when downstream operators require separate inputs.

---

## Reshape

**Category:** core  ·  **Since:** 0.1  ·  **Kind:** generic

Reshape a tensor while preserving the leading row dimension.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `x` | yes | no | tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | same_type(x) | reshape_preserve_rows(x,new_shape) | same_measure_level(x) |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `new_shape` | ints | yes |  |  |

### Validation Rules

- The leading row dimension N must be preserved.
- The product of trailing dimensions in new_shape must equal the product of trailing dimensions of x.

### Converter Notes

- Equivalent source operators: numpy reshape, TensorFlow/ONNX-style reshape patterns when preserving batch dimension, and framework-specific vector/matrix reshaping used in preprocessing.
- Coverage notes: Reshape changes trailing dimensions while preserving the leading row dimension N and total trailing element count. It does not reorder values beyond standard row-major reshape semantics.
- Lowering notes: Converters should use Reshape only when the source reshape has static shape and preserves batch rows. Dynamic reshape or data-dependent shape inference should be reported as unsupported or handled by an extension.

---

## TakeSlots

**Category:** core  ·  **Since:** 0.1  ·  **Kind:** generic

Select, reorder, and optionally duplicate slots from the expanded flat slot space of one or more inputs.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `xs` | yes | yes | tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | same_type(xs) | matrix(n_rows=N,n_cols=num_selected_slots) | derived_from_input_and_operator |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `indices` | ints | no |  |  |
| `names` | strings | no |  |  |

### Validation Rules

- Exactly one of indices or names must be present.
- If indices is present, indices refer to the expanded flat slot space derived from the input list.
- If names is present, names refer to visible slot names in the expanded flat slot space derived from the input list.
- Names must resolve uniquely within the visible scope.
- Selection may reorder and duplicate slots.
- All selected slots must have the same dtype.

### Converter Notes

- Equivalent source operators: sklearn column selection patterns, ColumnTransformer column subsets, Spark VectorSlicer, PMML field selection, and schema-based feature reordering.
- Coverage notes: TakeSlots selects, reorders, or duplicates slots from a homogeneous expanded flat slot space. It is intended for positional or name-based feature selection after schema expansion.
- Lowering notes: Use indices for positional source representations and names when schema-level feature names improve fidelity or readability. Use TakeSlots only when selected slots share a compatible dtype.

---

## Derive

**Category:** expression  ·  **Since:** 0.1  ·  **Kind:** generic

Produce derived column or tensor values from an embedded Expression.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `xs` | no | yes | column, matrix, numeric_tensor, string_tensor, boolean_tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | derived_from_expression(expr) | derived_from_expression(expr) | derived_from_expression(expr) |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `expr` | expression | yes |  |  |

### Validation Rules

- The expression must resolve only names visible in the node input namespace.
- Rank-1 inputs are interpreted as [N] columns.
- Rank-2 inputs are interpreted as [N, F] matrices whose trailing dimension contains logical columns.
- Tensor inputs may be referenced by name, but the expression must have a statically inferable output shape.
- The expression result must preserve the leading batch dimension N.
- The expression result must be a [N] column or a tensor whose first dimension is N.
- If inputs is empty, expr must be self-contained and must not reference any input columns or tensors.
- Derive must not perform reductions across rows, dynamic shape changes, row filtering, joins, aggregation, or arbitrary user-defined function execution.

### Converter Notes

- Equivalent source operators: PMML Apply / DefineFunction expressions used in DerivedField or OutputField; Spark ML SQLTransformer projection expressions; sklearn FunctionTransformer only when the callable can be lowered to deterministic element-wise, row-wise, or statically shaped tensor expressions.
- Coverage notes: Derive is intended for portable expression evaluation over fixed input columns, matrices, or tensors. It can represent element-wise tensor transforms such as log(X), X + c, fixed-column arithmetic such as X[:, 0] + X[:, 1], and statically shaped derived outputs. It does not represent arbitrary Python callables, Spark SQL UDFs, row filtering, aggregation, joins, or data-dependent output shape changes.
- Lowering notes: Converters may lower simple sklearn FunctionTransformer patterns such as numpy ufuncs, arithmetic expressions, fixed-column combinations, and shape-preserving matrix transforms. Matrix-level learned transforms or arbitrary numpy/Python code should be lowered to dedicated OMLE operators, custom extension operators, or reported as unsupported.

---

## Select

**Category:** core  ·  **Since:** 0.1  ·  **Kind:** generic

Select one of multiple candidate values using a row-wise selector.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `selector` | yes | no | integer_tensor | rank = 1 |
| `candidates` | yes | yes | tensor |  |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | same_type(candidates) | same_shape_as_candidates | derived_from_input_and_operator |  |

### Attributes

_(none)_

### Validation Rules

- All candidate inputs must have the same shape and dtype.
- selector must be a column of integer indices with shape [N].
- Each selector value must be in [0, num_candidates).
- Selection is row-wise and does not imply conditional graph execution.

### Converter Notes

- Equivalent source operators: row-wise choice expressions such as numpy choose/take_along_axis patterns, SQL CASE lowered to candidate selection, and framework condition-selection constructs after selector computation.
- Coverage notes: Select chooses among precomputed candidate tensors row by row using integer selector values. It does not imply conditional graph execution; all candidate inputs are computed before selection.
- Lowering notes: Converters should use Select when a source expression can be represented as selection among a fixed set of aligned candidates. Data-dependent control flow or branch execution should not be represented by Select.

---

## Clip

**Category:** core  ·  **Since:** 0.1  ·  **Kind:** generic

Clamp numeric values to a range.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `x` | yes | no | numeric_tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | same_type(x) | same_shape(x) | same_measure_level(x) |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `min` | float | no |  |  |
| `max` | float | no |  |  |

### Converter Notes

- Equivalent source operators: numpy clip, sklearn preprocessing clipping patterns, Spark SQL greatest/least combinations, and PMML outlier treatment as extreme values when expressible as clamping.
- Coverage notes: Clip clamps numeric tensor values to optional lower and upper bounds while preserving shape and dtype. At least one bound should normally be provided by converters.
- Lowering notes: Converters may use Clip for preprocessing ranges, PMML extreme-value outlier handling, or post-processing bounds. Missing-value handling should be represented separately, not by Clip.

---

## SparseToDense

**Category:** core  ·  **Since:** 0.1  ·  **Kind:** generic

Convert a sparse tensor to its dense tensor form.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `x` | yes | no | sparse_tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | dense_value_type(x) | same_dense_shape(x) | same_measure_level(x) |  |

### Attributes

_(none)_

### Validation Rules

- Input x must represent a sparse tensor with a declared dense shape [N, D] or more generally [N, ...].

### Converter Notes

- Equivalent source operators: sparse matrix densification in scipy/sklearn, Spark vector-to-dense conversions, and runtime fallback when an operator requires dense input.
- Coverage notes: SparseToDense materializes the dense tensor represented by a sparse input while preserving declared dense shape and value dtype.
- Lowering notes: Use SparseToDense when downstream OMLE operators do not support sparse input directly. Converters should be aware that densification can increase memory usage, especially for wide feature spaces.

---

## DenseToSparse

**Category:** core  ·  **Since:** 0.1  ·  **Kind:** generic

Convert a dense tensor to its sparse tensor form.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `x` | yes | no | tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | dense_to_sparse_value_type(x) | sparse_shape_from_dense(x) | same_measure_level(x) |  |

### Attributes

_(none)_

### Validation Rules

- Input x must have shape [N, D] or more generally [N, ...].
- The sparse output must preserve the declared dense shape of x.
- Only non-default values are materialized in the sparse representation.
- DenseToSparse uses the dtype default value as the implicit fill value for omitted entries.

### Converter Notes

- Equivalent source operators: dense-to-sparse conversions in scipy/sklearn or Spark sparse vector construction.
- Coverage notes: DenseToSparse materializes only non-default values and preserves the dense logical shape. The implicit fill value is the dtype default.
- Lowering notes: Use DenseToSparse when downstream operators can exploit sparse representation. Avoid adding it unless it improves compatibility or runtime efficiency.

---

## ArgMax

**Category:** selection  ·  **Since:** 0.1  ·  **Kind:** generic

Return the index of the maximum value in each row of a numeric matrix.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `x` | yes | no | numeric_tensor | rank = 2 |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | int64 | column | ORDINAL |  |

### Attributes

_(none)_

### Validation Rules

- Input x must have shape [N, K] with K >= 1.
- For each row, ArgMax returns the index of the maximum value.
- If multiple positions share the maximum value, the smallest index is returned.

### Converter Notes

- Equivalent source operators: numpy argmax, sklearn decision/probability decoding, Spark probability-to-prediction decoding, PMML max-score class selection.
- Coverage notes: ArgMax returns the smallest index of the maximum value for each row of a numeric matrix. It returns indices, not class labels.
- Lowering notes: Converters may use ArgMax to decode multiclass score, probability, or vote matrices. Add a label mapping step when the final prediction must be class labels rather than numeric indices.

---

## SelectByPrimarySecondaryScore

**Category:** selection  ·  **Since:** 0.1  ·  **Kind:** generic

Select one class index per row using primary scores first and secondary scores as tie-break.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `primary_scores` | yes | no | numeric_tensor | rank = 2 |
| `secondary_scores` | yes | no | numeric_tensor | rank = 2 |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | int64 | column | ORDINAL |  |

### Attributes

_(none)_

### Validation Rules

- primary_scores and secondary_scores must have the same shape [N, C].
- For each row, select the class with maximal primary score.
- If multiple classes are tied on primary score, select among them using maximal secondary score.
- If multiple classes are still tied, return the smallest class index.

### Converter Notes

- Equivalent source operators: sklearn OneVsOneClassifier prediction decoding that uses vote counts with confidence sums as a tie-break.
- Coverage notes: This operator selects a class index using primary scores first and secondary scores only for ties, with deterministic smallest-index tie-breaking.
- Lowering notes: Use this operator when a source OvO classifier requires both vote aggregation and confidence-based tie-breaking. For simple max-score decoding, use ArgMax instead.

---

## Sum

**Category:** reduction  ·  **Since:** 0.1  ·  **Kind:** generic

Elementwise sum of aligned tensors.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `xs` | yes | yes | numeric_tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | same_type_as_all_inputs | same_shape_as_all_inputs | CONTINUOUS |  |

### Attributes

_(none)_

### Converter Notes

- Equivalent source operators: element-wise tensor addition, PMML/Spark/sklearn ensemble score summation, and additive model score aggregation.
- Coverage notes: Sum performs element-wise summation over aligned numeric tensors with identical shape and dtype.
- Lowering notes: Converters may use Sum for additive ensembles, score accumulation, or combining independently computed numeric outputs. Use WeightedSum when source estimators have explicit weights.

---

## Average

**Category:** reduction  ·  **Since:** 0.1  ·  **Kind:** generic

Elementwise arithmetic mean of aligned tensors.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `xs` | yes | yes | numeric_tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | promote_to_float(inputs) | same_shape_as_all_inputs | CONTINUOUS |  |

### Attributes

_(none)_

### Converter Notes

- Equivalent source operators: element-wise mean aggregation, unweighted ensemble score averaging, and probability averaging when inputs are already aligned probabilities.
- Coverage notes: Average computes the arithmetic mean of aligned numeric tensors and promotes output to a floating dtype.
- Lowering notes: Converters may use Average for unweighted score or prediction aggregation. For class-probability ensemble voting, prefer SoftVote because it documents probability alignment semantics.

---

## WeightedSum

**Category:** reduction  ·  **Since:** 0.1  ·  **Kind:** generic

Elementwise weighted sum of aligned tensors.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `xs` | yes | yes | numeric_tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | promote_to_float(inputs) | same_shape_as_all_inputs | CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `weights` | floats | yes |  |  |

### Converter Notes

- Equivalent source operators: weighted additive ensemble aggregation, linear combination of model scores, and PMML/Spark/sklearn weighted score accumulation patterns.
- Coverage notes: WeightedSum computes the element-wise sum of each input multiplied by its corresponding weight. It does not normalize by the sum of weights.
- Lowering notes: Use WeightedSum when source semantics require raw weighted accumulation. Use WeightedAverage when the weighted result must be normalized by total weight.

---

## WeightedAverage

**Category:** reduction  ·  **Since:** 0.1  ·  **Kind:** generic

Elementwise weighted average of aligned tensors.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `xs` | yes | yes | numeric_tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | promote_to_float(inputs) | same_shape_as_all_inputs | CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `weights` | floats | yes |  |  |

### Converter Notes

- Equivalent source operators: weighted ensemble averaging, weighted probability averaging, and weighted mean score aggregation.
- Coverage notes: WeightedAverage computes the element-wise weighted mean of aligned numeric tensors and promotes output to a floating dtype.
- Lowering notes: Converters may use WeightedAverage for generic weighted numeric aggregation. For weighted soft-voting probabilities, prefer SoftVote when probability-specific validation and role metadata are desired.

---

## WeightedMedian

**Category:** reduction  ·  **Since:** 0.1  ·  **Kind:** generic

Elementwise weighted median across aligned numeric inputs.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `xs` | yes | yes | numeric_tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | promote_to_float(inputs) | same_shape_as_all_inputs | CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `weights` | floats | yes |  |  |

### Validation Rules

- All inputs must have the same shape.
- All inputs must be numeric.
- weights must have the same length as the number of inputs.
- All weights must be non-negative.
- At least one weight must be positive.
- For each output position, the weighted median is the smallest value whose cumulative sorted weight is at least half of the total weight.

### Converter Notes

- Equivalent source operators: sklearn AdaBoostRegressor prediction aggregation.
- Coverage notes: WeightedMedian computes the element-wise weighted median across aligned numeric inputs using non-negative estimator weights.
- Lowering notes: Use WeightedMedian to reproduce sklearn AdaBoostRegressor prediction semantics. Preserve estimator order and weights exactly to ensure deterministic tie behavior.

---

## Min

**Category:** reduction  ·  **Since:** 0.1  ·  **Kind:** generic

Elementwise minimum across aligned tensors.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `xs` | yes | yes | numeric_tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | same_type_as_all_inputs | same_shape_as_all_inputs | CONTINUOUS |  |

### Attributes

_(none)_

### Converter Notes

- Equivalent source operators: element-wise minimum operations such as numpy minimum/reduce, Spark least, PMML min-style Apply functions, and clipping lower-bound helper patterns.
- Coverage notes: Min computes the element-wise minimum across aligned numeric tensors with identical shape and dtype.
- Lowering notes: Converters may use Min for expression lowering, bounds logic, or ensemble/model post-processing when the source operation is an element-wise minimum.

---

## Max

**Category:** reduction  ·  **Since:** 0.1  ·  **Kind:** generic

Elementwise maximum across aligned tensors.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `xs` | yes | yes | numeric_tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | same_type_as_all_inputs | same_shape_as_all_inputs | CONTINUOUS |  |

### Attributes

_(none)_

### Converter Notes

- Equivalent source operators: element-wise maximum operations such as numpy maximum/reduce, Spark greatest, PMML max-style Apply functions, and clipping upper-bound helper patterns.
- Coverage notes: Max computes the element-wise maximum across aligned numeric tensors with identical shape and dtype.
- Lowering notes: Converters may use Max for expression lowering, bounds logic, or ensemble/model post-processing when the source operation is an element-wise maximum.

---

## Median

**Category:** reduction  ·  **Since:** 0.1  ·  **Kind:** generic

Elementwise median across aligned tensors.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `xs` | yes | yes | numeric_tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | promote_to_float(inputs) | same_shape_as_all_inputs | CONTINUOUS |  |

### Attributes

_(none)_

### Converter Notes

- Equivalent source operators: element-wise median aggregation across model outputs or numeric tensors.
- Coverage notes: Median computes the unweighted element-wise median across aligned numeric inputs and promotes output to a floating dtype.
- Lowering notes: Converters should use Median only when source inference semantics explicitly require median aggregation. Use WeightedMedian when estimator weights affect the median.

---

## MajorityVote

**Category:** voting  ·  **Since:** 0.1  ·  **Kind:** generic

Majority vote over aligned class-label columns.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `xs` | yes | yes | column |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | same_type_as_all_inputs | column | NOMINAL | PREDICTION |

### Attributes

_(none)_

### Converter Notes

- Equivalent source operators: sklearn VotingClassifier with voting='hard'; PMML MiningModel segmentation with majority-vote-style classification; generic hard-voting ensembles.
- Coverage notes: MajorityVote is prediction-only. It selects the class receiving the largest number of votes and does not produce probability outputs.
- Lowering notes: Use MajorityVote for unweighted hard class-label voting. Use WeightedMajorityVote for weighted hard voting, SoftVote for probability averaging, and SAMMEVote for SAMME-specific AdaBoost multiclass voting.

---

## WeightedMajorityVote

**Category:** voting  ·  **Since:** 0.1  ·  **Kind:** generic

Weighted majority vote over aligned class-label columns.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `xs` | yes | yes | column |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | same_type_as_all_inputs | column | NOMINAL | PREDICTION |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `weights` | floats | yes |  |  |

### Converter Notes

- Equivalent source operators: sklearn VotingClassifier with voting='hard' and weights; generic weighted hard-voting ensembles.
- Coverage notes: WeightedMajorityVote is prediction-only. It sums estimator weights by predicted class and selects the class with the largest total weight. Weighted vote totals are not probability estimates.
- Lowering notes: Use WeightedMajorityVote for generic weighted hard voting. Use SoftVote for probability averaging and SAMMEVote for SAMME AdaBoost multiclass semantics.

---

## SAMMEVote

**Category:** voting  ·  **Since:** 0.1  ·  **Kind:** generic

Aggregate classifier predictions using the SAMME multiclass AdaBoost voting rule.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `xs` | yes | yes | column |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule | Domain Rule |
|------|-----------|------------|--------------------|-----------|-------------|
| `prediction` | same_type_as_all_inputs | column | NOMINAL | PREDICTION |  |
| `probability` | float32_or_float64 | matrix(n_rows=N,n_cols=num_classes) | CONTINUOUS | PROBABILITY | probability_0_1 |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `weights` | floats | yes |  |  |
| `classes` | tensor_like | yes |  |  |

### Validation Rules

- Each input in xs must be a column with shape [N].
- All inputs in xs must have the same dtype and represent predictions over the same class space.
- weights must have the same length as the number of inputs.
- classes must provide the ordered class labels with shape [K], where K is the number of classes.
- K must be >= 2.
- For each row and each class, accumulate the sum of estimator weights for estimators whose predicted label equals that class.
- Convert accumulated class votes to class probabilities using softmax(votes / (K - 1)).
- The prediction output is the class label with maximum probability for each row.
- If multiple classes are tied after probability computation, the smallest class index in classes is selected.

### Converter Notes

- Equivalent source operators: sklearn AdaBoostClassifier with algorithm='SAMME' for multiclass classification.
- Coverage notes: SAMMEVote represents SAMME-specific multiclass voting semantics. It accumulates estimator weights by predicted class, computes probability with softmax(votes / (K - 1)), and returns the maximum-probability class. It is not equivalent to generic weighted majority voting.
- Lowering notes: Use SAMMEVote when converting SAMME-style AdaBoost ensembles whose base estimators output class predictions and whose estimator weights are accumulated by class. Use WeightedMajorityVote only for generic weighted hard voting.

---

## SoftVote

**Category:** voting  ·  **Since:** 0.1  ·  **Kind:** generic

Average or row-normalize aligned probability tensors across models.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `xs` | yes | yes | numeric_tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule | Domain Rule |
|------|-----------|------------|--------------------|-----------|-------------|
| `y` | promote_to_float(inputs) | same_shape_as_all_inputs | CONTINUOUS | PROBABILITY | probability_0_1 |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `weights` | floats | no |  |  |
| `normalize_rows` | bool | no | False |  |

### Validation Rules

- Input probability tensors must be class-aligned.
- All inputs must have the same shape.
- If weights is present, weights must have the same length as the number of inputs.
- SoftVote first computes the weighted elementwise sum of input probability tensors, or the unweighted elementwise sum when weights is absent.
- If normalize_rows is false, the weighted sum is divided by the sum of weights, or by the number of inputs when weights is absent.
- If normalize_rows is true, each output row is divided by its own row sum after accumulation.
- If normalize_rows is true, each row sum must be positive.
- normalize_rows must only be used for single-label multiclass probability normalization, not for multilabel marginal probabilities.

### Converter Notes

- Equivalent source operators: sklearn VotingClassifier with voting='soft'; probability-averaging ensemble patterns in PMML MiningModel segmentation; sklearn OneVsRestClassifier single-label multiclass probability normalization when normalize_rows=true.
- Coverage notes: SoftVote combines aligned probability tensors. By default, it computes ordinary weighted or unweighted soft voting by dividing accumulated probabilities by the total estimator weight or input count. When normalize_rows=true, it normalizes each row of the accumulated output so the row sums to 1.
- Lowering notes: Use normalize_rows=false for ordinary soft voting over already class-aligned probability distributions. Use normalize_rows=true for one-vs-rest multiclass probability assembly where independently produced class scores or probabilities must be normalized into a single multiclass probability distribution. Do not use normalize_rows=true for multilabel OneVsRestClassifier outputs, because multilabel probabilities are independent marginal probabilities and should not be forced to sum to 1.

---
