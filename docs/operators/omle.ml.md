# omle.ml — Operators

_ML model operators for OMLE v0.1._

**Registry version:** 0.1

## Operators

| Operator | Category | Kind | Summary |
|----------|----------|------|---------|
| [`Tree`](#tree) | tree | structured | Decision tree classifier or regressor. |
| [`TreeEnsemble`](#treeensemble) | ensemble | structured | Tree ensemble classifier or regressor. |
| [`Linear`](#linear) | linear | structured | Linear regressor or linear classifier. |
| [`SVM`](#svm) | svm | structured | Support vector machine classifier or regressor. |
| [`NeuralNetwork`](#neuralnetwork) | neural_network | structured | Feed-forward neural network classifier or regressor. |
| [`NaiveBayes`](#naivebayes) | probabilistic | structured | Naive Bayes classifier. |
| [`Clustering`](#clustering) | clustering | structured | Clustering model. |
| [`AnomalyDetection`](#anomalydetection) | anomaly_detection | structured | Anomaly detection model with algorithm-specific structured body variants. |
| [`KNN`](#knn) | instance_based | generic | k-nearest or radius-neighbors classifier or regressor. |

---

## Tree

**Category:** tree  ·  **Since:** 0.1  ·  **Kind:** structured  ·  **Body type:** `tree`

Decision tree classifier or regressor.

Structured body fields are defined by the Tree proto message. The model consumes the flattened slot sequence formed by concatenating all input tensors in input order. Probability output is available when the body task_type is binary or multiclass classification.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `xs` | yes | yes | numeric_tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule | Domain Rule |
|------|-----------|------------|--------------------|-----------|-------------|
| `prediction` | derived_from_body | derived_from_body | derived_from_body | PREDICTION |  |
| `probability` | derived_from_body | derived_from_body | CONTINUOUS | PROBABILITY | probability_0_1 |

### Attributes

_(none)_

### Validation Rules

- Each input in xs must have leading row dimension N.
- The tree body feature references are resolved against the flattened slot sequence formed by concatenating all inputs in order.

### Converter Notes

- Equivalent source operators: sklearn.tree.DecisionTreeClassifier; sklearn.tree.DecisionTreeRegressor; pyspark.ml.classification.DecisionTreeClassifier; pyspark.ml.regression.DecisionTreeRegressor; PMML TreeModel.
- Coverage notes: exact for the fitted split structure and leaf values. Probability output is meaningful only for classification task types.
- Lowering notes: the model consumes the flattened slot sequence formed by concatenating all inputs in order, so a converter may pass feature columns directly. Inserting an explicit Concat node first is permitted but not required.

---

## TreeEnsemble

**Category:** ensemble  ·  **Since:** 0.1  ·  **Kind:** structured  ·  **Body type:** `tree_ensemble`

Tree ensemble classifier or regressor.

Structured body fields are defined by the TreeEnsemble proto message. The model consumes the flattened slot sequence formed by concatenating all input tensors in input order. Probability output is available when the body task_type is binary or multiclass classification.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `xs` | yes | yes | numeric_tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule | Domain Rule |
|------|-----------|------------|--------------------|-----------|-------------|
| `prediction` | derived_from_body | derived_from_body | derived_from_body | PREDICTION |  |
| `probability` | derived_from_body | derived_from_body | CONTINUOUS | PROBABILITY | probability_0_1 |

### Attributes

_(none)_

### Validation Rules

- Each input in xs must have leading row dimension N.
- The tree ensemble body feature references are resolved against the flattened slot sequence formed by concatenating all inputs in order.

### Converter Notes

- Equivalent source operators: sklearn.ensemble.RandomForestClassifier/Regressor; sklearn.ensemble.ExtraTreesClassifier/Regressor; sklearn.ensemble.GradientBoostingClassifier/Regressor; sklearn.ensemble.HistGradientBoostingClassifier/Regressor; xgboost.Booster and the XGB* sklearn wrappers; lightgbm.Booster and the LGBM* sklearn wrappers; catboost.CatBoostClassifier/Regressor; pyspark.ml RandomForestClassificationModel/RandomForestRegressionModel/GBTClassificationModel/GBTRegressionModel; PMML MiningModel segmentation.
- Coverage notes: exact for the fitted trees, per-tree weights and base score. Probability output is meaningful only for classification task types; set post_transform to match the source framework's link function rather than pre-applying it to leaf values.
- Lowering notes: the model consumes the flattened slot sequence formed by concatenating all inputs in order. Inserting an explicit Concat node first is permitted but not required.
- Lowering notes: use tree_group to associate trees with class indices for multiclass boosting, and tree_weights for weighted ensembles such as AdaBoost-style aggregation.

---

## Linear

**Category:** linear  ·  **Since:** 0.1  ·  **Kind:** structured  ·  **Body type:** `linear`

Linear regressor or linear classifier.

Structured body fields are defined by the Linear proto message. The model consumes the flattened slot sequence formed by concatenating all input tensors in input order. Probability output is available when the body task_type is binary or multiclass classification.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `xs` | yes | yes | numeric_tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule | Domain Rule |
|------|-----------|------------|--------------------|-----------|-------------|
| `prediction` | derived_from_body | derived_from_body | derived_from_body | PREDICTION |  |
| `probability` | derived_from_body | derived_from_body | CONTINUOUS | PROBABILITY | probability_0_1 |

### Attributes

_(none)_

### Validation Rules

- Each input in xs must have leading row dimension N.
- The linear body coefficient layout is resolved against the flattened slot sequence formed by concatenating all inputs in order.

### Converter Notes

- Equivalent source operators: sklearn.linear_model.LinearRegression/Ridge/Lasso/ElasticNet/LogisticRegression/SGDClassifier/SGDRegressor; sklearn.linear_model.BayesianRidge and ARDRegression for the Bayesian posterior fields; pyspark.ml LinearRegressionModel/LogisticRegressionModel/GeneralizedLinearRegressionModel/LinearSVCModel; PMML RegressionModel and GeneralRegressionModel.
- Coverage notes: exact for coefficients and intercept. Probability output is available when the body task_type is binary or multiclass classification. weight_covariance and noise_precision carry the Bayesian posterior and are optional.
- Lowering notes: keep the source framework's coefficient layout — 1-D for regression and binary classification, 2-D [n_classes, n_features] for multiclass — and let n_outputs follow from it.
- Lowering notes: the model consumes the flattened slot sequence formed by concatenating all inputs in order. Inserting an explicit Concat node first is permitted but not required.

---

## SVM

**Category:** svm  ·  **Since:** 0.1  ·  **Kind:** structured  ·  **Body type:** `svm`

Support vector machine classifier or regressor.

Structured body fields are defined by the SVM proto message. The model consumes the flattened slot sequence formed by concatenating all input tensors in input order. Probability output is available only when the structured body represents classification with fitted probability parameters or calibrated probability support.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `xs` | yes | yes | numeric_tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule | Domain Rule |
|------|-----------|------------|--------------------|-----------|-------------|
| `prediction` | derived_from_body | derived_from_body | derived_from_body | PREDICTION |  |
| `probability` | derived_from_body | derived_from_body | CONTINUOUS | PROBABILITY | probability_0_1 |

### Attributes

_(none)_

### Validation Rules

- Each input in xs must have leading row dimension N.
- The SVM body feature layout is resolved against the flattened slot sequence formed by concatenating all inputs in order.
- Probability output is meaningful only for classification task types.
- If probability output is exposed, the structured body must contain the fitted probability-related parameters required by inference.

### Converter Notes

- Equivalent source operators: sklearn.svm.SVC/SVR/NuSVC/NuSVR/LinearSVC/LinearSVR; pyspark.ml.classification.LinearSVCModel; PMML SupportVectorMachineModel.
- Coverage notes: exact for support vectors, dual coefficients and intercepts. Use the linear body for LinearSVC/LinearSVR and the kernel body for the kernel-based estimators. Probability output requires Platt scaling parameters prob_a and prob_b, which are present only when the source estimator was fitted with probability estimation enabled.
- Lowering notes: set multiclass_strategy to match the source framework — sklearn SVC uses one-vs-one, LinearSVC uses one-vs-rest — because the decision-value layout differs between them.
- Lowering notes: the model consumes the flattened slot sequence formed by concatenating all inputs in order. Inserting an explicit Concat node first is permitted but not required.

---

## NeuralNetwork

**Category:** neural_network  ·  **Since:** 0.1  ·  **Kind:** structured  ·  **Body type:** `neural_network`

Feed-forward neural network classifier or regressor.

Structured body fields are defined by the NeuralNetwork proto message. The model consumes the flattened slot sequence formed by concatenating all input tensors in input order. Probability output is available when the structured body represents binary or multiclass classification with a probability-producing final activation or post-transform.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `xs` | yes | yes | numeric_tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule | Domain Rule |
|------|-----------|------------|--------------------|-----------|-------------|
| `prediction` | derived_from_body | derived_from_body | derived_from_body | PREDICTION |  |
| `probability` | derived_from_body | derived_from_body | CONTINUOUS | PROBABILITY | probability_0_1 |

### Attributes

_(none)_

### Validation Rules

- Each input in xs must have leading row dimension N.
- The neural network body feature layout is resolved against the flattened slot sequence formed by concatenating all inputs in order.
- Probability output is meaningful only for classification task types.
- If probability output is exposed, the final network layer or post-transform must define probability semantics.

### Converter Notes

- Equivalent source operators: sklearn.neural_network.MLPClassifier/MLPRegressor; pyspark.ml.classification.MultilayerPerceptronClassificationModel; PMML NeuralNetwork.
- Coverage notes: exact for dense feed-forward layers with per-layer activations. Limited to fully connected layers; convolutional, recurrent and attention architectures are out of scope for this operator.
- Lowering notes: NeuralNetwork has no post_transform field — the output activation is carried by the final layer's activation instead, so emit SOFTMAX or LOGISTIC there rather than as a separate transform.
- Lowering notes: the model consumes the flattened slot sequence formed by concatenating all inputs in order. Inserting an explicit Concat node first is permitted but not required.

---

## NaiveBayes

**Category:** probabilistic  ·  **Since:** 0.1  ·  **Kind:** structured  ·  **Body type:** `naive_bayes`

Naive Bayes classifier.

Structured body fields are defined by the NaiveBayes proto message. The model consumes the flattened slot sequence formed by concatenating all input tensors in input order.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `xs` | yes | yes | numeric_tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule | Domain Rule |
|------|-----------|------------|--------------------|-----------|-------------|
| `prediction` | derived_from_body | derived_from_body | derived_from_body | PREDICTION |  |
| `probability` | derived_from_body | derived_from_body | CONTINUOUS | PROBABILITY | probability_0_1 |

### Attributes

_(none)_

### Validation Rules

- Each input in xs must have leading row dimension N.
- The NaiveBayes body feature layout is resolved against the flattened slot sequence formed by concatenating all inputs in order.

### Converter Notes

- Equivalent source operators: sklearn.naive_bayes.GaussianNB/MultinomialNB/BernoulliNB/ComplementNB/CategoricalNB; pyspark.ml.classification.NaiveBayesModel; PMML NaiveBayesModel.
- Coverage notes: exact for fitted class priors and per-variant likelihood parameters. Exactly one implementation variant may be set. ComplementNB is lowered to the multinomial variant with its fitted complement weights.
- Lowering notes: store class_log_priors and the likelihood parameters in log space as the source framework does, rather than converting back to probabilities.
- Lowering notes: the model consumes the flattened slot sequence formed by concatenating all inputs in order. Inserting an explicit Concat node first is permitted but not required.

---

## Clustering

**Category:** clustering  ·  **Since:** 0.1  ·  **Kind:** structured  ·  **Body type:** `clustering`

Clustering model.

Structured body fields are defined by the Clustering proto message. The model consumes the flattened slot sequence formed by concatenating all input tensors in input order.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `xs` | yes | yes | numeric_tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `prediction` | derived_from_body | derived_from_body | derived_from_body | PREDICTION |

### Attributes

_(none)_

### Validation Rules

- Each input in xs must have leading row dimension N.
- The clustering body feature layout is resolved against the flattened slot sequence formed by concatenating all inputs in input order.

### Converter Notes

- Equivalent source operators: sklearn.cluster.KMeans/MiniBatchKMeans; sklearn.mixture.GaussianMixture; pyspark.ml.clustering.KMeansModel/GaussianMixtureModel; PMML ClusteringModel.
- Coverage notes: exact for fitted centroids, and for mixture weights, means and covariances. Use the prototype body for centroid-based clustering and the gaussian_mixture body for mixture models.
- Lowering notes: the primary output is a cluster identifier with role ENTITY_ID and INT32 dtype, not a prediction. Structured bodies may define additional semantic outputs such as distances or cluster scores according to their body contract.
- Lowering notes: the model consumes the flattened slot sequence formed by concatenating all inputs in order. Inserting an explicit Concat node first is permitted but not required.

---

## AnomalyDetection

**Category:** anomaly_detection  ·  **Since:** 0.1  ·  **Kind:** structured  ·  **Body type:** `anomaly_detection`

Anomaly detection model with algorithm-specific structured body variants.

Structured body fields are defined by the anomaly_detection proto message. The body contains anomaly_kind and an algorithm-specific structured variant such as isolation forest, local outlier factor, or elliptic envelope. LocalOutlierFactor is supported only for novelty-detection inference.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `xs` | yes | yes | numeric_tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `prediction` | derived_from_body | column | NOMINAL | PREDICTION |
| `score` | derived_from_body | column | CONTINUOUS | SCORE |
| `decision_value` | derived_from_body | column | CONTINUOUS | derived_from_body |

### Attributes

_(none)_

### Validation Rules

- Each input in xs must have leading row dimension N.
- The anomaly detection body feature layout is resolved against the flattened slot sequence formed by concatenating all inputs in order.
- The concrete inference semantics are determined by body.anomaly_kind and its corresponding structured sub-body.
- LocalOutlierFactor bodies must represent novelty-detection inference only.

### Converter Notes

- Equivalent source operators: sklearn.ensemble.IsolationForest; sklearn.neighbors.LocalOutlierFactor; sklearn.covariance.EllipticEnvelope; sklearn.svm.OneClassSVM and sklearn.linear_model.SGDOneClassSVM via the one_class_svm body; PMML AnomalyDetectionModel.
- Coverage notes: exact for the fitted detector state. One structured operator covers every family; the specific algorithm is selected by the body variant. The common output contract is prediction, score, and optional decision_value.
- Lowering notes: set mode to distinguish outlier detection (the training set may contain anomalies) from novelty detection, and set raw_score_polarity to record whether higher or lower raw scores mean more abnormal — these differ between source libraries and cannot be inferred from the scores alone.
- Lowering notes: the model consumes the flattened slot sequence formed by concatenating all inputs in order. Inserting an explicit Concat node first is permitted but not required.

---

## KNN

**Category:** instance_based  ·  **Since:** 0.1  ·  **Kind:** generic

k-nearest or radius-neighbors classifier or regressor.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `xs` | yes | yes | numeric_tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `prediction` | derived_from_knn_targets | column | derived_from_knn_targets | PREDICTION |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `train_features` | tensor_like | yes |  |  |
| `train_targets` | tensor_like | yes |  |  |
| `task_type` | string | yes |  | `regression`, `binary_classification`, `multiclass_classification` |
| `neighbor_mode` | string | no | k_neighbors | `k_neighbors`, `radius` |
| `n_neighbors` | int | no |  |  |
| `radius` | float | no |  |  |
| `metric` | string | no | minkowski | `euclidean`, `manhattan`, `minkowski`, `chebyshev`, `mahalanobis`, `seuclidean`, `cosine`, `haversine`, `precomputed` |
| `metric_param_names` | strings | no |  |  |
| `metric_param_values` | tensor_like | no |  |  |
| `weights` | string | no | uniform | `uniform`, `distance` |
| `empty_neighbor_policy` | string | no | error | `error`, `default_value` |
| `default_target` | tensor_like | no |  |  |
| `outlier_label` | tensor_like | no |  |  |

### Validation Rules

- Each input in xs must have leading row dimension N.
- The query feature layout is resolved against the flattened slot sequence formed by concatenating all inputs in order.
- If metric != 'precomputed', train_features must provide a rank-2 tensor with shape [M, D].
- If metric = 'precomputed', train_features must represent the fitted reference distance structure required by the chosen neighbor mode.
- train_targets must have leading dimension M.
- If metric != 'precomputed', the flattened trailing query feature dimension must equal D.
- If neighbor_mode = 'k_neighbors', n_neighbors is required, n_neighbors must be >= 1 and <= M, and radius must be absent or ignored.
- If neighbor_mode = 'radius', radius is required, radius must be > 0, and n_neighbors must be absent or ignored.
- If metric_param_names is present, metric_param_values must also be present.
- If metric_param_values is present, metric_param_names must also be present.
- metric_param_names and metric_param_values must have the same logical length.
- For metric = 'minkowski', metric_params may include parameter 'p'.
- For metric = 'mahalanobis', metric_params may include 'V' or 'VI' encoded in metric_param_values.
- For metric = 'seuclidean', metric_params may include parameter 'V' encoded in metric_param_values.
- If empty_neighbor_policy = 'default_value', default_target must be present.
- Callable metrics are not supported in OMLE v0.1.
- Callable weights are not supported in OMLE v0.1.
- For binary_classification or multiclass_classification, train_targets must represent class labels.
- For regression, train_targets must represent numeric target values.
- For radius mode classification, outlier_label may be used when no neighbors are found within radius.

### Converter Notes

- Equivalent source operators: sklearn.neighbors.KNeighborsClassifier/KNeighborsRegressor/RadiusNeighborsClassifier/RadiusNeighborsRegressor. sklearn.neighbors.NearestCentroid could be represented as k = 1 over class centroids, but no converter emits it today.
- Coverage notes: exact for the fitted reference dataset, distance metric and weighting. KNN is a generic operator — it has no dedicated proto body, so all fitted state travels as typed attributes and tensor references. Structured probability or score outputs may be added if OMLE standardizes KNN auxiliary outputs.
- Lowering notes: store the fitted reference dataset and target values as tensor entries, inline tensors, or sparse tensors; large reference sets should use tensor_ref so they are shared rather than duplicated.
- Lowering notes: the model consumes the flattened slot sequence formed by concatenating all inputs in order. Inserting an explicit Concat node first is permitted but not required.

---
