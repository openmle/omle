# omle.feature — Operators

_Feature preprocessing operators for OMLE v0.1._

**Registry version:** 0.1

## Operators

| Operator | Category | Kind | Summary |
|----------|----------|------|---------|
| [`StandardScaler`](#standardscaler) | scaling | generic | Standardize numeric inputs using fitted mean and scale values. |
| [`MinMaxScaler`](#minmaxscaler) | scaling | generic | Rescale numeric inputs into a configured target range. |
| [`RobustScaler`](#robustscaler) | scaling | generic | Scale numeric inputs using fitted robust center and scale statistics. |
| [`MaxAbsScaler`](#maxabsscaler) | scaling | generic | Scale numeric inputs by the fitted maximum absolute value per feature. |
| [`Normalizer`](#normalizer) | scaling | generic | Normalize rows according to a selected norm over the combined logical feature space. |
| [`PowerTransformer`](#powertransformer) | scaling | generic | Apply a fitted power transform independently to numeric feature inputs. |
| [`QuantileTransformer`](#quantiletransformer) | scaling | generic | Apply a fitted quantile-based transform independently to numeric feature inputs. |
| [`Bucketizer`](#bucketizer) | binning | generic | Map numeric inputs to ordinal bucket indices feature-wise. |
| [`Discretizer`](#discretizer) | binning | generic | Map numeric inputs to configured values according to interval bins. |
| [`NormContinuous`](#normcontinuous) | normalization | generic | Apply feature-wise piecewise linear normalization using ordered breakpoints. |
| [`SplineTransformer`](#splinetransformer) | basis_expansion | generic | Expand numeric features into B-spline basis features. |
| [`OneHotEncoder`](#onehotencoder) | encoding | generic | Map one or more categorical input columns to binary indicator matrices, one per input column. |
| [`OrdinalEncoder`](#ordinalencoder) | encoding | generic | Map one or more categorical input columns to ordinal indices or precomputed numeric lookup values. |
| [`LabelEncoder`](#labelencoder) | encoding | generic | Map one or more nominal label inputs to integer identifiers. |
| [`NormDiscrete`](#normdiscrete) | encoding | generic | Map a column to a binary indicator for equality with one target value. |
| [`MapValues`](#mapvalues) | lookup | generic | Map input values to output values by exact-match lookup. |
| [`TargetEncoder`](#targetencoder) | encoding | generic | Map one or more categorical input columns to precomputed target-encoding values. |
| [`LabelBinarizer`](#labelbinarizer) | encoding | generic | Binarize labels in a one-vs-all fashion. |
| [`MultiLabelBinarizer`](#multilabelbinarizer) | encoding | generic | Convert per-row label sets to a binary indicator matrix. |
| [`PolynomialFeatures`](#polynomialfeatures) | basis_expansion | generic | Generate polynomial and interaction features from the flattened numeric feature space. |
| [`TruncatedSVD`](#truncatedsvd) | dimensionality_reduction | generic | Project the flattened numeric feature space to a lower-dimensional latent space using fitted truncated singular vectors. |
| [`FastICA`](#fastica) | dimensionality_reduction | generic | Project the flattened numeric feature space to independent components using a fitted ICA transform. |
| [`FactorAnalysis`](#factoranalysis) | dimensionality_reduction | generic | Project the flattened numeric feature space to latent factors using a fitted factor analysis transform. |
| [`KernelPCA`](#kernelpca) | dimensionality_reduction | generic | Project the flattened numeric feature space to a lower-dimensional latent space using a fitted kernel PCA transform. |
| [`SparsePCA`](#sparsepca) | dimensionality_reduction | generic | Project the flattened numeric feature space to sparse latent components using a fitted sparse PCA transform. |
| [`NMF`](#nmf) | dimensionality_reduction | generic | Project the flattened non-negative numeric feature space to a latent space using a fitted non-negative matrix factorization transform. |
| [`LatentDirichletAllocation`](#latentdirichletallocation) | topic_modeling | generic | Project the flattened document-term feature space to document-topic features using a fitted latent Dirichlet allocation transform. |
| [`Imputer`](#imputer) | missing | generic | Replace missing values in one or more inputs with configured fitted fill values. |
| [`Binarizer`](#binarizer) | threshold | generic | Convert numeric inputs to binary indicator values using per-column thresholds. |
| [`MissingIndicator`](#missingindicator) | missing | generic | Generate binary indicators for missing values across the logical feature space. |
| [`KNNImputer`](#knnimputer) | missing | generic | Impute missing numeric values using nearest neighbors from the fitted training data. |

---

## StandardScaler

**Category:** scaling  ·  **Since:** 0.1  ·  **Kind:** generic

Standardize numeric inputs using fitted mean and scale values.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, numeric_tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `ys` | promote_to_float(corresponding_input) | same_shape_as_corresponding_input | CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values | Description |
|------|------|----------|---------|-------------|-------------|
| `mean` | tensor_like | no |  |  | Per-feature centering values. Omitted when the source transformer disabled centering (Spark withMean=false, sklearn with_mean=False); consumers then skip centering. |
| `scale` | tensor_like | no |  |  | Per-feature scaling values. Omitted when the source transformer disabled scaling (Spark withStd=false, sklearn with_std=False); consumers then skip scaling. |

### Validation Rules

- At least one input must be present in xs.
- All inputs in xs must have the same leading row dimension N.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- Let F be the total number of logical input columns contributed by xs.
- mean and scale, when present, must be numeric tensors compatible with F.
- The number of outputs in ys must equal the number of inputs in xs.
- Output ys[i] corresponds to input xs[i].
- Each output ys[i] must preserve the shape of xs[i].
- Scaling is applied independently to each logical input column.

### Converter Notes

- Equivalent source operators: sklearn.preprocessing.StandardScaler; pyspark.ml.feature.StandardScaler.
- Coverage notes: exact for fitted inference parameters mean and scale.
- Lowering notes: multiple logical input columns may be supplied either as one matrix or as mixed column and matrix inputs.
- Lowering notes: multiple inputs remain separate; ys[i] preserves the boundary and shape of xs[i].

---

## MinMaxScaler

**Category:** scaling  ·  **Since:** 0.1  ·  **Kind:** generic

Rescale numeric inputs into a configured target range.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, numeric_tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `ys` | promote_to_float(corresponding_input) | same_shape_as_corresponding_input | CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `data_min` | tensor_like | yes |  |  |
| `data_max` | tensor_like | yes |  |  |
| `feature_range_min` | float | no | 0.0 |  |
| `feature_range_max` | float | no | 1.0 |  |

### Validation Rules

- At least one input must be present in xs.
- All inputs in xs must have the same leading row dimension N.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- Let F be the total number of logical input columns contributed by xs.
- data_min and data_max must be numeric tensors compatible with F.
- The number of outputs in ys must equal the number of inputs in xs.
- Output ys[i] corresponds to input xs[i].
- Each output ys[i] must preserve the shape of xs[i].
- Scaling is applied independently to each logical input column.

### Converter Notes

- Equivalent source operators: sklearn.preprocessing.MinMaxScaler; pyspark.ml.feature.MinMaxScaler.
- Coverage notes: exact for fitted inference parameters data_min, data_max, and feature range.
- Lowering notes: multiple logical input columns may be supplied either as one matrix or as mixed column and matrix inputs.
- Lowering notes: multiple inputs remain separate; ys[i] preserves the boundary and shape of xs[i].

---

## RobustScaler

**Category:** scaling  ·  **Since:** 0.1  ·  **Kind:** generic

Scale numeric inputs using fitted robust center and scale statistics.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, numeric_tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `ys` | promote_to_float(corresponding_input) | same_shape_as_corresponding_input | CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `center` | tensor_like | yes |  |  |
| `scale` | tensor_like | yes |  |  |

### Validation Rules

- At least one input must be present in xs.
- All inputs in xs must have the same leading row dimension N.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- Let F be the total number of logical input columns contributed by xs.
- center and scale must be numeric tensors compatible with F.
- The number of outputs in ys must equal the number of inputs in xs.
- Output ys[i] corresponds to input xs[i].
- Each output ys[i] must preserve the shape of xs[i].
- Scaling is applied independently to each logical input column.

### Converter Notes

- Equivalent source operators: sklearn.preprocessing.RobustScaler.
- Coverage notes: exact for fitted inference parameters center and scale.
- Lowering notes: no direct built-in Spark ML, PMML, or category_encoders equivalent is assumed.
- Lowering notes: multiple inputs remain separate; ys[i] preserves the boundary and shape of xs[i].

---

## MaxAbsScaler

**Category:** scaling  ·  **Since:** 0.1  ·  **Kind:** generic

Scale numeric inputs by the fitted maximum absolute value per feature.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, numeric_tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `ys` | promote_to_float(corresponding_input) | same_shape_as_corresponding_input | CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `scale` | tensor_like | yes |  |  |

### Validation Rules

- At least one input must be present in xs.
- All inputs in xs must have the same leading row dimension N.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- Let F be the total number of logical input columns contributed by xs.
- scale must be a numeric tensor compatible with F.
- The number of outputs in ys must equal the number of inputs in xs.
- Output ys[i] corresponds to input xs[i].
- Each output ys[i] must preserve the shape of xs[i].
- Scaling is applied independently to each logical input column.

### Converter Notes

- Equivalent source operators: sklearn.preprocessing.MaxAbsScaler; pyspark.ml.feature.MaxAbsScaler.
- Coverage notes: exact for fitted inference parameter scale.
- Lowering notes: multiple logical input columns may be supplied either as one matrix or as mixed column and matrix inputs.
- Lowering notes: multiple inputs remain separate; ys[i] preserves the boundary and shape of xs[i].

---

## Normalizer

**Category:** scaling  ·  **Since:** 0.1  ·  **Kind:** generic

Normalize rows according to a selected norm over the combined logical feature space.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, numeric_tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | promote_to_float(xs) | matrix(n_rows=N,n_cols=num_logical_input_columns) | CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `norm` | string | no | l2 | `l1`, `l2`, `max` |

### Validation Rules

- Each input in xs must have leading row dimension N.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- Let F be the total number of logical input columns contributed by xs.
- The operator first forms the flattened feature vector of width F for each row, then applies row normalization across that full vector.
- The output matrix y has shape [N, F].

### Converter Notes

- Equivalent source operators: sklearn.preprocessing.Normalizer; pyspark.ml.feature.Normalizer.
- Coverage notes: exact for row-wise normalization semantics.
- Lowering notes: the operator flattens all logical input columns into one feature vector per row before applying the selected norm.

---

## PowerTransformer

**Category:** scaling  ·  **Since:** 0.1  ·  **Kind:** generic

Apply a fitted power transform independently to numeric feature inputs.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, numeric_tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `ys` | promote_to_float(corresponding_input) | same_shape_as_corresponding_input | CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `method` | string | yes |  | `box_cox`, `yeo_johnson` |
| `lambdas` | tensor_like | yes |  |  |
| `standardize` | bool | no | True |  |
| `mean` | tensor_like | no |  |  |
| `scale` | tensor_like | no |  |  |

### Validation Rules

- At least one input must be present in xs.
- All inputs in xs must have the same leading row dimension N.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- Let F be the total number of logical input columns contributed by xs.
- lambdas must provide a floating-point tensor compatible with F.
- If standardize = true, mean and scale must both be present and compatible with F.
- If standardize = false, mean and scale must be absent or ignored.
- If method = 'box_cox', all input values must be strictly positive.
- The power transform is applied feature-wise using the fitted lambda values.
- If standardize = true, the transformed values are standardized using the fitted mean and scale.
- The number of outputs in ys must equal the number of inputs in xs.
- Output ys[i] corresponds to input xs[i].
- Each output ys[i] must preserve the shape of xs[i].

### Converter Notes

- Equivalent source operators: sklearn.preprocessing.PowerTransformer.
- Coverage notes: exact for fitted inference parameters of Box-Cox and Yeo-Johnson transforms.
- Lowering notes: only fitted inference parameters are exported; training-time estimation details are not represented.
- Lowering notes: multiple inputs remain separate; ys[i] preserves the boundary and shape of xs[i].

---

## QuantileTransformer

**Category:** scaling  ·  **Since:** 0.1  ·  **Kind:** generic

Apply a fitted quantile-based transform independently to numeric feature inputs.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, numeric_tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `ys` | promote_to_float(corresponding_input) | same_shape_as_corresponding_input | CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `quantiles` | tensor_like | yes |  |  |
| `references` | tensor_like | yes |  |  |
| `output_distribution` | string | yes |  | `uniform`, `normal` |

### Validation Rules

- At least one input must be present in xs.
- All inputs in xs must have the same leading row dimension N.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- Let F be the total number of logical input columns contributed by xs.
- quantiles must provide a floating-point tensor of shape [Q, F] or equivalent compatible form.
- references must provide a floating-point tensor of shape [Q].
- Q must be >= 2.
- Each logical input column is transformed independently using the fitted quantile landmarks and references.
- If output_distribution = 'uniform', the output is the interpolated cumulative probability.
- If output_distribution = 'normal', the output is the inverse-normal transform of the interpolated cumulative probability.
- The number of outputs in ys must equal the number of inputs in xs.
- Output ys[i] corresponds to input xs[i].
- Each output ys[i] must preserve the shape of xs[i].

### Converter Notes

- Equivalent source operators: sklearn.preprocessing.QuantileTransformer.
- Coverage notes: exact for fitted inference parameters quantiles, references, and output distribution.
- Lowering notes: only fitted quantile landmarks and references are exported; training-time sampling details are not represented.
- Lowering notes: multiple inputs remain separate; ys[i] preserves the boundary and shape of xs[i].

---

## Bucketizer

**Category:** binning  ·  **Since:** 0.1  ·  **Kind:** generic

Map numeric inputs to ordinal bucket indices feature-wise.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, numeric_tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `ys` | int64 | same_shape_as_corresponding_input | ORDINAL |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `boundaries` | tensor_like | yes |  |  |
| `boundary_offsets` | tensor_like | yes |  |  |

### Validation Rules

- At least one input must be present in xs.
- All inputs in xs must have the same leading row dimension N.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- Let F be the total number of logical input columns contributed by xs.
- boundaries must provide a rank-1 tensor containing concatenated boundary lists across logical input columns.
- boundary_offsets must provide an integer tensor of shape [F + 1].
- For logical input column j, its boundary list is boundaries[boundary_offsets[j] : boundary_offsets[j + 1]].
- Bucketization is applied independently to each logical input column.
- The number of outputs in ys must equal the number of inputs in xs.
- Output ys[i] corresponds to input xs[i].
- Each output ys[i] must preserve the shape of xs[i].

### Converter Notes

- Equivalent source operators: pyspark.ml.feature.Bucketizer; sklearn.preprocessing.KBinsDiscretizer with ordinal encoding.
- Coverage notes: exact for bucket-index style inference.
- Lowering notes: Supports one matrix with multiple columns, multiple single-column inputs, or mixed input forms.
- Lowering notes: multiple inputs remain separate; ys[i] preserves the boundary and shape of xs[i].

---

## Discretizer

**Category:** binning  ·  **Since:** 0.1  ·  **Kind:** generic

Map numeric inputs to configured values according to interval bins.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, numeric_tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `ys` | same_type(attr:output_dtype) | same_shape_as_corresponding_input | derived_from_input_and_operator |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `bin_left` | tensor_like | yes |  |  |
| `bin_right` | tensor_like | yes |  |  |
| `left_closed` | tensor_like | yes |  |  |
| `right_closed` | tensor_like | yes |  |  |
| `bin_values` | tensor_like | yes |  |  |
| `bin_offsets` | tensor_like | yes |  |  |
| `default_value` | scalar | no |  |  |
| `map_missing_to` | scalar | no |  |  |
| `output_dtype` | string | yes |  |  |

### Validation Rules

- At least one input must be present in xs.
- All inputs in xs must have the same leading row dimension N.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- Let F be the total number of logical input columns contributed by xs.
- bin_left, bin_right, left_closed, right_closed, and bin_values must provide concatenated interval definitions across logical input columns.
- bin_offsets must provide an integer tensor of shape [F + 1].
- For logical input column j, its interval definitions are sliced by bin_offsets[j] : bin_offsets[j + 1].
- Within each logical input column, intervals should be non-overlapping.
- For each input value, the first matching interval for that logical input column determines the output.
- If no interval matches, default_value is used when present; otherwise the result is missing.
- If map_missing_to is present, missing input values map to that value.
- The number of outputs in ys must equal the number of inputs in xs.
- Output ys[i] corresponds to input xs[i].
- Each output ys[i] must preserve the shape of xs[i].

### Converter Notes

- Equivalent source operators: PMML Discretize; sklearn.preprocessing.KBinsDiscretizer only for partial interval-binning analogies.
- Coverage notes: exact for interval-to-value lookup semantics, including default and missing mapping.
- Lowering notes: Use Bucketizer instead when only ordinal bin indices are needed.
- Lowering notes: multiple inputs remain separate; ys[i] preserves the boundary and shape of xs[i].

---

## NormContinuous

**Category:** normalization  ·  **Since:** 0.1  ·  **Kind:** generic

Apply feature-wise piecewise linear normalization using ordered breakpoints.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, numeric_tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `ys` | promote_to_float(corresponding_input) | same_shape_as_corresponding_input | CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `orig_points` | tensor_like | yes |  |  |
| `norm_points` | tensor_like | yes |  |  |
| `point_offsets` | tensor_like | yes |  |  |
| `outlier_treatment` | string | no | as_is | `as_is`, `as_missing_values`, `as_extreme_values` |
| `map_missing_to` | scalar | no |  |  |

### Validation Rules

- At least one input must be present in xs.
- All inputs in xs must have the same leading row dimension N.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- Let F be the total number of logical input columns contributed by xs.
- orig_points and norm_points must provide rank-1 tensors containing concatenated breakpoint definitions across all logical input columns.
- point_offsets must provide an integer tensor of shape [F + 1].
- For logical input column j, its breakpoint pairs are defined by orig_points[point_offsets[j] : point_offsets[j + 1]] and norm_points[point_offsets[j] : point_offsets[j + 1]].
- orig_points and norm_points must have the same total length.
- Each logical input column must have at least two breakpoint pairs.
- Within each logical input column, orig_points must be strictly increasing.
- If outlier_treatment = 'as_is', values below the first orig_point extrapolate linearly using the first segment and values above the last orig_point extrapolate linearly using the last segment.
- If outlier_treatment = 'as_extreme_values', values below the first orig_point map to the first norm_point and values above the last orig_point map to the last norm_point.
- If outlier_treatment = 'as_missing_values', values outside the breakpoint range are treated as missing values.
- If an input value is missing and map_missing_to is present, the output is map_missing_to.
- If an input value is missing and map_missing_to is absent, the output is missing.
- If outlier_treatment = 'as_missing_values' and an outlier is encountered, map_missing_to is used when present; otherwise the output is missing.
- For an input value between two adjacent orig_points, output is computed by linear interpolation between the corresponding norm_points.
- The number of outputs in ys must equal the number of inputs in xs.
- Output ys[i] corresponds to input xs[i].
- Each output ys[i] must preserve the shape of xs[i].

### Converter Notes

- Equivalent source operators: PMML NormContinuous.
- Coverage notes: exact for PMML piecewise linear interpolation semantics, including missing-value and outlier-treatment behavior.
- Lowering notes: Supports one matrix with multiple columns, multiple single-column inputs, or mixed input forms.
- Lowering notes: multiple inputs remain separate; ys[i] preserves the boundary and shape of xs[i].

---

## SplineTransformer

**Category:** basis_expansion  ·  **Since:** 0.1  ·  **Kind:** generic

Expand numeric features into B-spline basis features.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, numeric_tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | promote_to_float(xs) | derived_from_input_and_operator | CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `knots` | tensor_like | yes |  |  |
| `degree` | int | yes |  |  |
| `include_bias` | bool | no | True |  |
| `extrapolation` | string | no | constant | `error`, `constant`, `linear`, `continue`, `periodic` |

### Validation Rules

- Each input in xs must have leading row dimension N.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- Let F be the total number of logical input columns contributed by xs.
- knots must provide a floating-point tensor compatible with the fitted spline basis definition.
- degree must be >= 0.
- The spline basis is evaluated feature-wise using the fitted knot vectors.
- Output feature count is determined by the fitted knots, degree, number of logical input columns, and include_bias.
- The extrapolation attribute controls behavior outside the fitted knot range.

### Converter Notes

- Equivalent source operators: sklearn.preprocessing.SplineTransformer.
- Coverage notes: exact for fitted spline basis inference semantics.
- Lowering notes: The operator preserves sklearn-compatible basis ordering.

---

## OneHotEncoder

**Category:** encoding  ·  **Since:** 0.1  ·  **Kind:** generic

Map one or more categorical input columns to binary indicator matrices, one per input column.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, string_tensor, integer_tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule | Domain Rule |
|------|-----------|------------|--------------------|-----------|-------------|
| `ys` | same_type(attr:output_dtype) | derived_from_corresponding_input_and_operator | FLAG |  | binary_0_1 |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `categories` | tensor_like | yes |  |  |
| `category_offsets` | tensor_like | yes |  |  |
| `output_dtype` | string | no | FLOAT32 | `FLOAT32`, `FLOAT64`, `INT32`, `INT64` |

### Validation Rules

- Each input in xs must have leading row dimension N.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- Let F be the number of inputs in xs.
- categories must provide a rank-1 tensor containing the concatenated category vocabulary across all inputs.
- category_offsets must provide an integer tensor of shape [F + 1].
- For input column i, its category list is categories[category_offsets[i] : category_offsets[i + 1]].
- Each input is encoded independently into one binary indicator matrix ys[i] of shape [N, K_i] where K_i = category_offsets[i+1] - category_offsets[i].

### Converter Notes

- Equivalent source operators: sklearn.preprocessing.OneHotEncoder; pyspark.ml.feature.OneHotEncoder; category_encoders.OneHotEncoder.
- Coverage notes: exact for fitted one-hot category lookup; each input column produces its own output matrix.
- Lowering notes: For single-column encoding, category_offsets typically has shape [2]. Use tensor_ref for large shared vocabularies and inline tensor for small local vocabularies.

---

## OrdinalEncoder

**Category:** encoding  ·  **Since:** 0.1  ·  **Kind:** generic

Map one or more categorical input columns to ordinal indices or precomputed numeric lookup values.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, string_tensor, integer_tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `ys` | int64_if_attr_absent_else_same_type(encoded_values) | same_shape_as_corresponding_input | ORDINAL_if_attr_absent_else_CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `categories` | tensor_like | yes |  |  |
| `category_offsets` | tensor_like | yes |  |  |
| `encoded_values` | tensor_like | no |  |  |
| `default_values` | tensor_like | no |  |  |

### Validation Rules

- At least one input must be present in xs.
- All inputs in xs must have the same leading row dimension N.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- Let F be the total number of logical input columns contributed by xs.
- categories must provide a rank-1 tensor containing the concatenated category vocabulary across all logical input columns.
- category_offsets must provide an integer tensor of shape [F + 1].
- For logical input column j, its category list is categories[category_offsets[j] : category_offsets[j + 1]].
- If encoded_values is absent, each logical input column is encoded independently using the zero-based local category index within that column.
- If encoded_values is present, encoded_values must provide a numeric tensor aligned one-to-one with categories and having the same total logical length as categories.
- If encoded_values is present, each known category maps to its corresponding entry in encoded_values instead of its ordinal index.
- If default_values is present, default_values must provide a numeric tensor of shape [F] giving the per-feature fallback for unseen categories.
- If default_values is present, encoded_values must also be present.
- If encoded_values is present and an unseen category is encountered for logical input column f, default_values[f] is used when default_values is present; otherwise the result is missing or follows the runtime unknown-category policy.
- The number of outputs in ys must equal the number of inputs in xs.
- Output ys[i] corresponds to input xs[i].
- Each output ys[i] must preserve the shape of xs[i].

### Converter Notes

- Equivalent source operators: sklearn.preprocessing.OrdinalEncoder; pyspark.ml.feature.StringIndexer as the closest Spark ML analogue; category_encoders.OrdinalEncoder.
- Coverage notes: exact for fitted category lookup tables; Spark StringIndexer ordering policies may require converter-specific preprocessing.
- Lowering notes: Supports one matrix with multiple columns, multiple single-column inputs, or mixed input forms. Without encoded_values, this matches standard ordinal encoding semantics. With encoded_values, this operator performs per-category numeric lookup using the same category tables.
- Lowering notes: multiple inputs remain separate; ys[i] preserves the boundary and shape of xs[i].

---

## LabelEncoder

**Category:** encoding  ·  **Since:** 0.1  ·  **Kind:** generic

Map one or more nominal label inputs to integer identifiers.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, string_tensor, integer_tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `ys` | int64 | same_shape_as_corresponding_input | NOMINAL |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `labels` | tensor_like | yes |  |  |
| `label_offsets` | tensor_like | yes |  |  |

### Validation Rules

- At least one input must be present in xs.
- All inputs in xs must have the same leading row dimension N.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- Let F be the total number of logical input columns contributed by xs.
- labels must provide a rank-1 tensor containing the concatenated label vocabulary across all logical input columns.
- label_offsets must provide an integer tensor of shape [F + 1].
- For logical input column j, its label list is labels[label_offsets[j] : label_offsets[j + 1]].
- Each logical input column is encoded independently to one nominal integer-ID logical output column.
- Encoded integer IDs are nominal identifiers and do not imply semantic order.
- The number of outputs in ys must equal the number of inputs in xs.
- Output ys[i] corresponds to input xs[i].
- Each output ys[i] must preserve the shape of xs[i].

### Converter Notes

- Equivalent source operators: sklearn.preprocessing.LabelEncoder for single-target style usage; pyspark.ml.feature.StringIndexer as the closest Spark ML analogue.
- Coverage notes: exact for nominal label-to-id lookup semantics across logical input columns.
- Lowering notes: Supports one matrix with multiple columns, multiple single-column inputs, or mixed input forms. Unlike OrdinalEncoder, the encoded integer IDs are nominal rather than ordinal.
- Lowering notes: multiple inputs remain separate; ys[i] preserves the boundary and shape of xs[i].

---

## NormDiscrete

**Category:** encoding  ·  **Since:** 0.1  ·  **Kind:** generic

Map a column to a binary indicator for equality with one target value.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `x` | yes | no | column |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule | Domain Rule |
|------|-----------|------------|--------------------|-----------|-------------|
| `y` | same_type(attr:output_dtype) | same_shape(x) | FLAG |  | binary_0_1 |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `value` | scalar | yes |  |  |
| `map_missing_to` | scalar | no |  |  |
| `output_dtype` | string | no | INT64 | `INT32`, `INT64`, `FLOAT32`, `FLOAT64` |

### Validation Rules

- If x equals value, output is 1; otherwise output is 0.
- If map_missing_to is present, missing input values map to that value instead of normal equality semantics.
- map_missing_to must be compatible with output_dtype.

### Converter Notes

- Equivalent source operators: PMML NormDiscrete.
- Coverage notes: exact for single-value indicator semantics, including missing-value override.
- Lowering notes: no direct built-in sklearn, Spark ML, or category_encoders equivalent is assumed.

---

## MapValues

**Category:** lookup  ·  **Since:** 0.1  ·  **Kind:** generic

Map input values to output values by exact-match lookup.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `x` | yes | no | column |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | same_type(attr:output_dtype) | same_shape(x) | derived_from_input_and_operator |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `keys` | tensor_like | yes |  |  |
| `values` | tensor_like | yes |  |  |
| `default_value` | scalar | no |  |  |
| `map_missing_to` | scalar | no |  |  |
| `output_dtype` | string | yes |  |  |

### Validation Rules

- keys and values must provide tensors with the same leading dimension K.
- keys must be rank-1.
- values must be rank-1.
- Lookup uses exact equality matching.
- If no key matches, default_value is used when present; otherwise the result is missing.
- If map_missing_to is present, missing input values map to that value.

### Converter Notes

- Equivalent source operators: PMML MapValues.
- Coverage notes: exact for single-key dictionary-style lookup semantics.
- Lowering notes: This v0.1 form supports single-key lookup. Multi-key lookup may be added in a future version.

---

## TargetEncoder

**Category:** encoding  ·  **Since:** 0.1  ·  **Kind:** generic

Map one or more categorical input columns to precomputed target-encoding values.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, string_tensor, integer_tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | same_type(encoded_values) | derived_from_input_and_operator | CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `categories` | tensor_like | yes |  |  |
| `category_offsets` | tensor_like | yes |  |  |
| `encoded_values` | tensor_like | yes |  |  |
| `default_values` | tensor_like | yes |  |  |
| `target_kind` | string | yes |  | `regression`, `binary`, `multiclass` |

### Validation Rules

- Each input in xs must have leading row dimension N.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- Let F be the total number of logical input columns contributed by xs.
- categories must provide a rank-1 tensor containing the concatenated category vocabulary across all logical input columns.
- category_offsets must provide an integer tensor of shape [F + 1].
- For logical input column j, its category list is categories[category_offsets[j] : category_offsets[j + 1]].
- If target_kind is 'regression' or 'binary', encoded_values must provide a floating-point tensor of shape [C_total] and default_values must provide a floating-point tensor of shape [F].
- If target_kind is 'multiclass', encoded_values must provide a floating-point tensor of shape [C_total, K] and default_values must provide a floating-point tensor of shape [F, K].
- default_values must have dtype compatible with encoded_values.
- Lookup uses exact equality matching independently for each logical input column.
- If an input value matches a category for its logical input column, output uses the corresponding encoded value.
- If an input value does not match any category or is missing, output uses the default_values for that logical input column.
- If target_kind is 'regression' or 'binary', the output matrix has shape [N, F].
- If target_kind is 'multiclass', the output has K columns per logical input column, concatenated in logical input column order.

### Converter Notes

- Equivalent source operators: sklearn.preprocessing.TargetEncoder; category_encoders.TargetEncoder.
- Coverage notes: exact for exported fitted lookup tables for regression, binary, and multiclass target encoding.
- Lowering notes: Supports one matrix with multiple columns, multiple single-column inputs, or mixed input forms. Export the fitted target-encoding values directly; do not export training-time smoothing or cross-fitting logic. For multiclass target encoding, each logical input column expands to one block of K output columns.

---

## LabelBinarizer

**Category:** encoding  ·  **Since:** 0.1  ·  **Kind:** generic

Binarize labels in a one-vs-all fashion.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `x` | yes | no | column |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | same_type(attr:output_dtype) | derived_from_input_and_operator | FLAG |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `classes` | tensor_like | yes |  |  |
| `neg_label` | int | no | 0 |  |
| `pos_label` | int | no | 1 |  |
| `output_dtype` | string | no | INT64 | `INT32`, `INT64`, `FLOAT32`, `FLOAT64` |

### Validation Rules

- classes must provide a tensor of shape [K].
- K must be >= 2.
- If K = 2, output shape is [N] and y[i] = pos_label when x[i] equals classes[1], else neg_label.
- If K > 2, output shape is [N, K] and y[i, j] = pos_label when x[i] equals classes[j], else neg_label.
- If x[i] does not match any class, all outputs for that row are neg_label.

### Converter Notes

- Equivalent source operators: sklearn.preprocessing.LabelBinarizer.
- Coverage notes: exact for one-vs-all label binarization semantics, including the binary special case.
- Lowering notes: This operator is target-oriented and should not be replaced by OneHotEncoder.

---

## MultiLabelBinarizer

**Category:** encoding  ·  **Since:** 0.1  ·  **Kind:** generic

Convert per-row label sets to a binary indicator matrix.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `x` | yes | no | label_set_sequence |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule | Domain Rule |
|------|-----------|------------|--------------------|-----------|-------------|
| `y` | same_type(attr:output_dtype) | matrix(n_rows=N,n_cols=K) | FLAG |  | binary_0_1 |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `classes` | tensor_like | yes |  |  |
| `output_dtype` | string | no | INT64 | `INT32`, `INT64`, `FLOAT32`, `FLOAT64` |

### Validation Rules

- classes must provide a tensor of shape [K].
- K must be >= 1.
- For each row i and class j, y[i, j] = 1 if classes[j] is present in x[i], else 0.
- Duplicate labels within the same input row do not increase the output value beyond 1.
- Labels not present in classes are ignored.

### Converter Notes

- Equivalent source operators: sklearn.preprocessing.MultiLabelBinarizer.
- Coverage notes: exact for per-row label-set to binary-indicator expansion.
- Lowering notes: This operator requires a collection-valued input kind such as label_set_sequence.

---

## PolynomialFeatures

**Category:** basis_expansion  ·  **Since:** 0.1  ·  **Kind:** generic

Generate polynomial and interaction features from the flattened numeric feature space.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, numeric_tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | promote_to_float(xs) | derived_from_input_and_operator | CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `min_degree` | int | no | 0 |  |
| `max_degree` | int | yes |  |  |
| `interaction_only` | bool | no | False |  |
| `include_bias` | bool | no | True |  |

### Validation Rules

- Each input in xs must have leading row dimension N.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- The operator first forms the flattened feature space from all logical input columns, then generates polynomial and interaction features over that full space.
- min_degree must be >= 0.
- max_degree must be >= 0.
- max_degree must be >= min_degree.
- If include_bias = false, the constant bias term is omitted.
- If interaction_only = true, only interaction terms with distinct logical input columns are produced.
- Output feature count and ordering follow the fitted polynomial expansion definition.

### Converter Notes

- Equivalent source operators: sklearn.preprocessing.PolynomialFeatures.
- Coverage notes: exact for fitted polynomial and interaction feature generation semantics.
- Lowering notes: The operator preserves sklearn-compatible output ordering.

---

## TruncatedSVD

**Category:** dimensionality_reduction  ·  **Since:** 0.1  ·  **Kind:** generic

Project the flattened numeric feature space to a lower-dimensional latent space using fitted truncated singular vectors.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, numeric_tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | promote_to_float(xs) | derived_from_input_and_operator | CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `components` | tensor_like | yes |  |  |

### Validation Rules

- Each input in xs must have leading row dimension N.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- Let F be the total number of logical input columns contributed by xs.
- The operator first forms the flattened feature space of width F, then applies the fitted linear projection.
- components must provide a floating-point tensor compatible with F.

### Converter Notes

- Equivalent source operators: sklearn.decomposition.TruncatedSVD.
- Coverage notes: exact for fitted linear latent-space projection inference.
- Lowering notes: Only fitted inference parameters are exported; training-time solver details are not represented.

---

## FastICA

**Category:** dimensionality_reduction  ·  **Since:** 0.1  ·  **Kind:** generic

Project the flattened numeric feature space to independent components using a fitted ICA transform.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, numeric_tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | promote_to_float(xs) | derived_from_input_and_operator | CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `mean` | tensor_like | no |  |  |
| `whitening` | tensor_like | no |  |  |
| `components` | tensor_like | yes |  |  |

### Validation Rules

- Each input in xs must have leading row dimension N.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- Let F be the total number of logical input columns contributed by xs.
- The operator first forms the flattened feature space of width F, then applies centering, optional whitening, and the fitted ICA projection.
- components must provide a floating-point tensor compatible with F.
- If mean is present, it must be compatible with F.
- If whitening is present, it must be compatible with the fitted preprocessing step used before applying components.

### Converter Notes

- Equivalent source operators: sklearn.decomposition.FastICA.
- Coverage notes: exact for fitted ICA transform inference.
- Lowering notes: Converters should export the fitted transform in the exact form needed to reproduce sklearn-compatible output.

---

## FactorAnalysis

**Category:** dimensionality_reduction  ·  **Since:** 0.1  ·  **Kind:** generic

Project the flattened numeric feature space to latent factors using a fitted factor analysis transform.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, numeric_tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | promote_to_float(xs) | derived_from_input_and_operator | CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `mean` | tensor_like | yes |  |  |
| `components` | tensor_like | yes |  |  |
| `noise_variance` | tensor_like | no |  |  |

### Validation Rules

- Each input in xs must have leading row dimension N.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- Let F be the total number of logical input columns contributed by xs.
- The operator first forms the flattened feature space of width F, then applies the fitted factor-analysis transform.
- mean must provide a floating-point tensor compatible with F.
- components must provide a floating-point tensor compatible with F.
- If noise_variance is present, it must be compatible with F.

### Converter Notes

- Equivalent source operators: sklearn.decomposition.FactorAnalysis.
- Coverage notes: exact for fitted factor-analysis transform inference.
- Lowering notes: Converters should export the fitted parameters needed to reproduce sklearn-compatible transform output.

---

## KernelPCA

**Category:** dimensionality_reduction  ·  **Since:** 0.1  ·  **Kind:** generic

Project the flattened numeric feature space to a lower-dimensional latent space using a fitted kernel PCA transform.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, numeric_tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | promote_to_float(xs) | derived_from_input_and_operator | CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `fit_samples` | tensor_like | yes |  |  |
| `dual_components` | tensor_like | yes |  |  |
| `kernel` | string | yes |  | `linear`, `poly`, `rbf`, `sigmoid`, `cosine`, `precomputed` |
| `gamma` | float | no |  |  |
| `degree` | int | no |  |  |
| `coef0` | float | no |  |  |
| `kernel_center_row_mean` | tensor_like | no |  |  |
| `kernel_center_all_mean` | tensor_like | no |  |  |

### Validation Rules

- Each input in xs must have leading row dimension N.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- Let F be the total number of logical input columns contributed by xs.
- The operator first forms the flattened feature space of width F, then applies the fitted kernel map and dual projection.
- If kernel != 'precomputed', fit_samples must provide a floating-point tensor compatible with F.
- dual_components must provide a floating-point tensor compatible with the fitted kernel basis.
- If kernel = 'precomputed', the runtime input must represent precomputed kernel rows against the fitted samples.
- If kernel centering statistics are present, they must be compatible with the fitted kernel centering procedure.

### Converter Notes

- Equivalent source operators: sklearn.decomposition.KernelPCA.
- Coverage notes: exact for fitted kernel PCA transform inference.
- Lowering notes: Only fitted inference parameters are exported; training-time eigensolver details are not represented.

---

## SparsePCA

**Category:** dimensionality_reduction  ·  **Since:** 0.1  ·  **Kind:** generic

Project the flattened numeric feature space to sparse latent components using a fitted sparse PCA transform.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, numeric_tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | promote_to_float(xs) | derived_from_input_and_operator | CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `mean` | tensor_like | no |  |  |
| `components` | tensor_like | yes |  |  |

### Validation Rules

- Each input in xs must have leading row dimension N.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- Let F be the total number of logical input columns contributed by xs.
- The operator first forms the flattened feature space of width F, then applies the fitted sparse PCA transform.
- components must provide a floating-point tensor compatible with F.
- If mean is present, it must be compatible with F.

### Converter Notes

- Equivalent source operators: sklearn.decomposition.SparsePCA.
- Coverage notes: exact for fitted sparse PCA transform inference.
- Lowering notes: Converters should export the fitted transform parameters needed to reproduce sklearn-compatible output.

---

## NMF

**Category:** dimensionality_reduction  ·  **Since:** 0.1  ·  **Kind:** generic

Project the flattened non-negative numeric feature space to a latent space using a fitted non-negative matrix factorization transform.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, numeric_tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | promote_to_float(xs) | derived_from_input_and_operator | CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `components` | tensor_like | yes |  |  |

### Validation Rules

- Each input in xs must have leading row dimension N.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- Let F be the total number of logical input columns contributed by xs.
- The operator first forms the flattened feature space of width F, then applies the fitted NMF transform.
- All input values must be non-negative.
- components must provide a floating-point tensor compatible with F.

### Converter Notes

- Equivalent source operators: sklearn.decomposition.NMF.
- Coverage notes: exact for fitted NMF transform inference.
- Lowering notes: Only fitted inference parameters are exported; training-time factorization details are not represented.

---

## LatentDirichletAllocation

**Category:** topic_modeling  ·  **Since:** 0.1  ·  **Kind:** generic

Project the flattened document-term feature space to document-topic features using a fitted latent Dirichlet allocation transform.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, numeric_tensor, sparse_tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | promote_to_float(xs) | derived_from_input_and_operator | CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `components` | tensor_like | yes |  |  |
| `doc_topic_prior` | float | no |  |  |
| `topic_word_prior` | float | no |  |  |

### Validation Rules

- Each input in xs must have leading row dimension N.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- Let F be the total number of logical input columns contributed by xs.
- The operator first forms the flattened document-term feature space of width F, then applies the fitted LDA transform.
- Input values must be non-negative document-term features.
- components must provide a floating-point tensor compatible with F.

### Converter Notes

- Equivalent source operators: sklearn.decomposition.LatentDirichletAllocation.
- Coverage notes: exact for fitted document-topic transform inference.
- Lowering notes: This operator is intended for fitted transform semantics only; training-time variational learning details are not represented.

---

## Imputer

**Category:** missing  ·  **Since:** 0.1  ·  **Kind:** generic

Replace missing values in one or more inputs with configured fitted fill values.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `ys` | same_type_as_corresponding_input | same_shape_as_corresponding_input | same_measure_level_as_corresponding_input |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `fill_value` | scalar | no |  |  |
| `fill_tensor` | tensor_like | no |  |  |

### Validation Rules

- At least one input must be present in xs.
- All inputs in xs must have the same leading row dimension N.
- Exactly one of fill_value or fill_tensor must be provided.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- Let F be the total number of logical input columns contributed by xs.
- The number of outputs in ys must equal the number of inputs in xs.
- Output ys[i] corresponds to input xs[i].
- Each output ys[i] must preserve the dtype, shape, and measure level of xs[i].
- If fill_value is present, it must be coercible to the dtype of every input to which it is applied.
- If fill_tensor is present, it must provide fitted fill values compatible with the F logical feature slots contributed by xs.
- Missing-value replacement is applied independently to each logical feature slot.

### Converter Notes

- Equivalent source operators: sklearn.impute.SimpleImputer for fixed fitted fill values; pyspark.ml.feature.Imputer for fitted mean or median numeric imputation.
- Coverage notes: exact for runtime missing-value substitution using exported fill values.
- Lowering notes: converters may lower framework-specific mean, median, most-frequent, or constant strategies into explicit fill_value or fill_tensor parameters.
- Lowering notes: multiple inputs remain separate; ys[i] preserves the boundary and shape of xs[i].

---

## Binarizer

**Category:** threshold  ·  **Since:** 0.1  ·  **Kind:** generic

Convert numeric inputs to binary indicator values using per-column thresholds.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, numeric_tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule | Domain Rule |
|------|-----------|------------|--------------------|-----------|-------------|
| `ys` | same_type(attr:output_dtype) | same_shape_as_corresponding_input | FLAG |  | binary_0_1 |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `thresholds` | tensor_like | yes |  |  |
| `output_dtype` | string | no | INT64 | `INT32`, `INT64`, `FLOAT32`, `FLOAT64` |

### Validation Rules

- At least one input must be present in xs.
- All inputs in xs must have the same leading row dimension N.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- Let F be the number of inputs in xs.
- thresholds must be a rank-1 tensor of shape [F], one threshold per input.
- Binarization is applied independently to each input: xs[i] >= thresholds[i] → 1, else 0.
- The number of outputs in ys must equal the number of inputs in xs.
- Output ys[i] corresponds to input xs[i].
- Each output ys[i] must preserve the shape of xs[i].

### Converter Notes

- Equivalent source operators: sklearn.preprocessing.Binarizer; pyspark.ml.feature.Binarizer.
- Coverage notes: exact for threshold-based binary conversion semantics.
- Lowering notes: For a single-column encoder, thresholds has shape [1]. Use the same value for all columns to replicate a uniform threshold.
- Lowering notes: multiple inputs remain separate; ys[i] preserves the boundary and shape of xs[i].

---

## MissingIndicator

**Category:** missing  ·  **Since:** 0.1  ·  **Kind:** generic

Generate binary indicators for missing values across the logical feature space.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule | Domain Rule |
|------|-----------|------------|--------------------|-----------|-------------|
| `y` | same_type(attr:output_dtype) | derived_from_input_and_operator | FLAG |  | binary_0_1 |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `features_mode` | string | no | missing_only | `missing_only`, `all` |
| `feature_indices` | tensor_like | no |  |  |
| `error_on_new` | bool | no | True |  |
| `output_dtype` | string | no | INT64 | `INT32`, `INT64`, `FLOAT32`, `FLOAT64` |

### Validation Rules

- Each input in xs must have leading row dimension N.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- Let F be the total number of logical input columns contributed by xs.
- If features_mode = 'all', output contains one indicator column per logical input column.
- If features_mode = 'missing_only', feature_indices must provide an INT tensor listing the logical input columns that had missing values at fit time.
- If features_mode = 'missing_only', output contains one indicator column for each logical input column listed in feature_indices, in that order.
- If error_on_new = true and features_mode = 'missing_only', runtime must raise or signal an error when a logical input column not listed in feature_indices contains missing values.
- If error_on_new = false and features_mode = 'missing_only', missing values in logical input columns not listed in feature_indices do not add new output columns.
- Each output value is 1 when the corresponding logical input column is missing, else 0.

### Converter Notes

- Equivalent source operators: sklearn.impute.MissingIndicator.
- Coverage notes: exact for fitted missing-indicator generation semantics.
- Lowering notes: converters should resolve the fitted feature selection and export feature_indices explicitly when features_mode = 'missing_only'.

---

## KNNImputer

**Category:** missing  ·  **Since:** 0.1  ·  **Kind:** generic

Impute missing numeric values using nearest neighbors from the fitted training data.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `xs` | yes | yes | column, matrix, numeric_tensor | rank in {1,2} |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `ys` | promote_to_float(corresponding_input) | same_shape_as_corresponding_input | CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `train_features` | tensor_like | yes |  |  |
| `n_neighbors` | int | yes |  |  |
| `weights` | string | no | uniform | `uniform`, `distance` |
| `metric` | string | no | nan_euclidean | `nan_euclidean` |
| `keep_empty_features` | bool | no | False |  |

### Validation Rules

- At least one input must be present in xs.
- All inputs in xs must have the same leading row dimension N.
- Each rank-1 input contributes one logical input column.
- Each rank-2 input contributes its trailing column dimension logical input columns in order.
- Let F be the total number of logical input columns contributed by xs.
- The operator forms the logical feature space of width F for neighbor-distance computation while preserving the original input boundaries in its outputs.
- train_features must provide a numeric rank-2 tensor of shape [M, F].
- n_neighbors must be >= 1 and <= M.
- metric = 'nan_euclidean' computes distances using only jointly observed logical feature columns and ignores columns missing in either row.
- Observed input values pass through unchanged.
- For each missing logical feature value, neighbors are selected from training rows using the configured metric.
- If weights = 'uniform', the imputed value is the arithmetic mean of the selected neighbor values that are observed for that logical feature column.
- If weights = 'distance', the imputed value is the distance-weighted mean of the selected neighbor values that are observed for that logical feature column.
- If no selected neighbor has an observed value for a missing logical feature column, the runtime behavior must follow the fitted sklearn-compatible policy represented by keep_empty_features.
- If keep_empty_features = true, logical feature columns that are entirely missing in the fitted training data are retained in the output.
- The number of outputs in ys must equal the number of inputs in xs.
- Output ys[i] corresponds to input xs[i].
- Each output ys[i] must preserve the shape of xs[i].

### Converter Notes

- Equivalent source operators: sklearn.impute.KNNImputer.
- Coverage notes: exact for fitted nearest-neighbor imputation semantics using exported training features.
- Lowering notes: converters should export the fitted training feature matrix directly in train_features. Converters may still insert an explicit Concat node before KNNImputer, but it is not required.
- Lowering notes: multiple inputs remain separate in the output even though all logical feature columns participate jointly in neighbor-distance computation.

---
