"""Structured model body IR classes: Linear, NaiveBayes variants, Tree, TreeEnsemble,
Clustering variants, SVM variants, NeuralNetwork, AnomalyDetection."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from ._util import enum_from_dict, int_from_dict, ints_from_dict, obj_to_dict
from .enums import (
    CovarianceType,
    DetectionMode,
    DistanceMeasure,
    NeuralNetworkActivation,
    PostTransform,
    ScorePolarity,
    SVMKernelType,
    SVMMulticlassStrategy,
    TaskType,
    TreeAggregation,
    TreeNodeKind,
    TreeSplitOp,
)
from .predicate import Predicate
from .types import Scalar, TensorValue

# ── Linear ────────────────────────────────────────────────────────────────────

@dataclass
class Linear:
    """Structured linear model body."""

    task_type: TaskType = TaskType.TASK_TYPE_UNSPECIFIED
    coefficients: TensorValue = field(default_factory=TensorValue)
    intercept: Optional[TensorValue] = None
    weight_covariances: Optional[TensorValue] = None
    noise_precision: Optional[TensorValue] = None
    post_transform: PostTransform = PostTransform.POST_TRANSFORM_UNSPECIFIED

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Linear":
        return cls(
            task_type=enum_from_dict(TaskType, d.get("task_type")),
            coefficients=TensorValue.from_dict(d.get("coefficients", {})),
            intercept=TensorValue.from_dict(d["intercept"]) if "intercept" in d else None,
            weight_covariances=TensorValue.from_dict(d["weight_covariances"]) if "weight_covariances" in d else None,
            noise_precision=TensorValue.from_dict(d["noise_precision"]) if "noise_precision" in d else None,
            post_transform=enum_from_dict(PostTransform, d.get("post_transform")),
        )


# ── Naive Bayes ───────────────────────────────────────────────────────────────

@dataclass
class GaussianNaiveBayes:
    means: TensorValue = field(default_factory=TensorValue)
    variances: TensorValue = field(default_factory=TensorValue)
    variance_epsilon: Optional[Scalar] = None

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "GaussianNaiveBayes":
        return cls(
            means=TensorValue.from_dict(d.get("means", {})),
            variances=TensorValue.from_dict(d.get("variances", {})),
            variance_epsilon=Scalar.from_dict(d["variance_epsilon"]) if "variance_epsilon" in d else None,
        )


@dataclass
class MultinomialNaiveBayes:
    feature_log_prob: TensorValue = field(default_factory=TensorValue)

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "MultinomialNaiveBayes":
        return cls(feature_log_prob=TensorValue.from_dict(d.get("feature_log_prob", {})))


@dataclass
class BernoulliNaiveBayes:
    feature_log_prob: TensorValue = field(default_factory=TensorValue)
    binarize_threshold: Optional[Scalar] = None

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "BernoulliNaiveBayes":
        return cls(
            feature_log_prob=TensorValue.from_dict(d.get("feature_log_prob", {})),
            binarize_threshold=Scalar.from_dict(d["binarize_threshold"]) if "binarize_threshold" in d else None,
        )


@dataclass
class CategoricalNaiveBayes:
    category_log_prob: TensorValue = field(default_factory=TensorValue)
    category_offset: list[int] = field(default_factory=list)
    category_count: list[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "CategoricalNaiveBayes":
        return cls(
            category_log_prob=TensorValue.from_dict(d.get("category_log_prob", {})),
            category_offset=list(d.get("category_offset", [])),
            category_count=list(d.get("category_count", [])),
        )


@dataclass
class NaiveBayes:
    """Structured Naive Bayes body (oneof implementation)."""

    task_type: TaskType = TaskType.TASK_TYPE_UNSPECIFIED
    class_log_priors: TensorValue = field(default_factory=TensorValue)
    gaussian: Optional[GaussianNaiveBayes] = None
    multinomial: Optional[MultinomialNaiveBayes] = None
    bernoulli: Optional[BernoulliNaiveBayes] = None
    categorical: Optional[CategoricalNaiveBayes] = None

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "NaiveBayes":
        return cls(
            task_type=enum_from_dict(TaskType, d.get("task_type")),
            class_log_priors=TensorValue.from_dict(d.get("class_log_priors", {})),
            gaussian=GaussianNaiveBayes.from_dict(d["gaussian"]) if "gaussian" in d else None,
            multinomial=MultinomialNaiveBayes.from_dict(d["multinomial"])
                if "multinomial" in d else None,
            bernoulli=BernoulliNaiveBayes.from_dict(d["bernoulli"]) if "bernoulli" in d else None,
            categorical=CategoricalNaiveBayes.from_dict(d["categorical"])
                if "categorical" in d else None,
        )


# ── Tree & TreeEnsemble ───────────────────────────────────────────────────────

@dataclass
class ComplexPredicate:
    node_index: int = 0
    predicate: Optional[Predicate] = None

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "ComplexPredicate":
        return cls(
            node_index=d.get("node_index", 0),
            predicate=Predicate.from_dict(d["predicate"]) if "predicate" in d else None,
        )


@dataclass
class Tree:
    """Flat-array decision tree representation."""

    task_type: TaskType = TaskType.TASK_TYPE_UNSPECIFIED
    num_nodes: int = 0
    node_kind: list[TreeNodeKind] = field(default_factory=list)
    split_feature: list[int] = field(default_factory=list)
    split_threshold: Optional[TensorValue] = None
    split_op: list[TreeSplitOp] = field(default_factory=list)
    category_set_offset: list[int] = field(default_factory=list)
    category_set_count: list[int] = field(default_factory=list)
    category_set: list[int] = field(default_factory=list)
    complex_predicates: list[ComplexPredicate] = field(default_factory=list)
    children_index: list[int] = field(default_factory=list)
    children_offset: list[int] = field(default_factory=list)
    children_count: list[int] = field(default_factory=list)
    default_child: list[int] = field(default_factory=list)
    leaf_value: Optional[TensorValue] = None
    leaf_width: int = 0
    leaf_vector: Optional[TensorValue] = None
    leaf_vector_index: list[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Tree":
        return cls(
            task_type=enum_from_dict(TaskType, d.get("task_type")),
            num_nodes=d.get("num_nodes", 0),
            node_kind=[enum_from_dict(TreeNodeKind, k) for k in d.get("node_kind", [])],
            split_feature=list(d.get("split_feature", [])),
            split_threshold=TensorValue.from_dict(d["split_threshold"]) if "split_threshold" in d else None,
            split_op=[enum_from_dict(TreeSplitOp, op) for op in d.get("split_op", [])],
            category_set_offset=list(d.get("category_set_offset", [])),
            category_set_count=list(d.get("category_set_count", [])),
            category_set=list(d.get("category_set", [])),
            complex_predicates=[ComplexPredicate.from_dict(p)
                                 for p in d.get("complex_predicates", [])],
            children_index=list(d.get("children_index", [])),
            children_offset=list(d.get("children_offset", [])),
            children_count=list(d.get("children_count", [])),
            default_child=list(d.get("default_child", [])),
            leaf_value=TensorValue.from_dict(d["leaf_value"]) if "leaf_value" in d else None,
            leaf_width=d.get("leaf_width", 0),
            leaf_vector=TensorValue.from_dict(d["leaf_vector"]) if "leaf_vector" in d else None,
            leaf_vector_index=list(d.get("leaf_vector_index", [])),
        )


@dataclass
class TreeEnsemble:
    """Structured tree ensemble body."""

    task_type: TaskType = TaskType.TASK_TYPE_UNSPECIFIED
    trees: list[Tree] = field(default_factory=list)
    aggregation: TreeAggregation = TreeAggregation.AGGREGATION_UNSPECIFIED
    post_transform: PostTransform = PostTransform.POST_TRANSFORM_UNSPECIFIED
    tree_weights: Optional[TensorValue] = None
    base_score: Optional[Scalar] = None
    tree_group: list[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "TreeEnsemble":
        return cls(
            task_type=enum_from_dict(TaskType, d.get("task_type")),
            trees=[Tree.from_dict(t) for t in d.get("trees", [])],
            aggregation=enum_from_dict(TreeAggregation, d.get("aggregation")),
            post_transform=enum_from_dict(PostTransform, d.get("post_transform")),
            tree_weights=TensorValue.from_dict(d["tree_weights"]) if "tree_weights" in d else None,
            base_score=Scalar.from_dict(d["base_score"]) if "base_score" in d else None,
            tree_group=list(d.get("tree_group", [])),
        )


# ── Clustering ────────────────────────────────────────────────────────────────

@dataclass
class PrototypeClustering:
    centers: TensorValue = field(default_factory=TensorValue)
    distance_measure: DistanceMeasure = DistanceMeasure.DISTANCE_MEASURE_UNSPECIFIED
    cluster_labels: list[Scalar] = field(default_factory=list)

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "PrototypeClustering":
        return cls(
            centers=TensorValue.from_dict(d.get("centers", {})),
            distance_measure=enum_from_dict(DistanceMeasure, d.get("distance_measure")),
            cluster_labels=[Scalar.from_dict(s) for s in d.get("cluster_labels", [])],
        )


@dataclass
class GaussianMixtureClustering:
    weights: TensorValue = field(default_factory=TensorValue)
    means: TensorValue = field(default_factory=TensorValue)
    covariances: TensorValue = field(default_factory=TensorValue)
    covariance_type: CovarianceType = CovarianceType.COVARIANCE_TYPE_UNSPECIFIED
    component_labels: list[Scalar] = field(default_factory=list)

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "GaussianMixtureClustering":
        return cls(
            weights=TensorValue.from_dict(d.get("weights", {})),
            means=TensorValue.from_dict(d.get("means", {})),
            covariances=TensorValue.from_dict(d.get("covariances", {})),
            covariance_type=enum_from_dict(CovarianceType, d.get("covariance_type")),
            component_labels=[Scalar.from_dict(s) for s in d.get("component_labels", [])],
        )


@dataclass
class Clustering:
    """Structured clustering body (oneof implementation)."""

    task_type: TaskType = TaskType.TASK_TYPE_UNSPECIFIED
    prototype: Optional[PrototypeClustering] = None
    gaussian_mixture: Optional[GaussianMixtureClustering] = None

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Clustering":
        return cls(
            task_type=enum_from_dict(TaskType, d.get("task_type")),
            prototype=PrototypeClustering.from_dict(d["prototype"])
                if "prototype" in d else None,
            gaussian_mixture=GaussianMixtureClustering.from_dict(d["gaussian_mixture"])
                if "gaussian_mixture" in d else None,
        )


# ── SVM ───────────────────────────────────────────────────────────────────────

@dataclass
class LinearSVM:
    """Linear SVM parameters."""

    coefficients: TensorValue = field(default_factory=TensorValue)
    intercept: Optional[TensorValue] = None

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "LinearSVM":
        return cls(
            coefficients=TensorValue.from_dict(d.get("coefficients", {})),
            intercept=TensorValue.from_dict(d["intercept"]) if "intercept" in d else None,
        )


@dataclass
class KernelSVM:
    """Kernel SVM parameters."""

    kernel_type: SVMKernelType = SVMKernelType.KERNEL_TYPE_UNSPECIFIED
    support_vectors: TensorValue = field(default_factory=TensorValue)
    dual_coefficients: TensorValue = field(default_factory=TensorValue)
    intercept: Optional[TensorValue] = None
    gamma: Optional[Scalar] = None
    degree: Optional[int] = None
    coef0: Optional[Scalar] = None
    n_support: list[int] = field(default_factory=list)
    prob_a: Optional[TensorValue] = None  # Platt scaling A params (sklearn probA_)
    prob_b: Optional[TensorValue] = None  # Platt scaling B params (sklearn probB_)

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "KernelSVM":
        return cls(
            kernel_type=enum_from_dict(SVMKernelType, d.get("kernel_type")),
            support_vectors=TensorValue.from_dict(d.get("support_vectors", {})),
            dual_coefficients=TensorValue.from_dict(d.get("dual_coefficients", {})),
            intercept=TensorValue.from_dict(d["intercept"]) if "intercept" in d else None,
            gamma=Scalar.from_dict(d["gamma"]) if "gamma" in d else None,
            degree=d.get("degree"),
            coef0=Scalar.from_dict(d["coef0"]) if "coef0" in d else None,
            n_support=ints_from_dict(d.get("n_support")),
            prob_a=TensorValue.from_dict(d["prob_a"]) if "prob_a" in d else None,
            prob_b=TensorValue.from_dict(d["prob_b"]) if "prob_b" in d else None,
        )


@dataclass
class SVM:
    """Structured support vector machine body (oneof: linear or kernel)."""

    task_type: TaskType = TaskType.TASK_TYPE_UNSPECIFIED
    post_transform: PostTransform = PostTransform.POST_TRANSFORM_UNSPECIFIED
    multiclass_strategy: Optional[SVMMulticlassStrategy] = None
    linear: Optional[LinearSVM] = None
    kernel: Optional[KernelSVM] = None

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "SVM":
        return cls(
            task_type=enum_from_dict(TaskType, d.get("task_type")),
            post_transform=enum_from_dict(PostTransform, d.get("post_transform")),
            multiclass_strategy=enum_from_dict(SVMMulticlassStrategy,
                d.get("multiclass_strategy")) if "multiclass_strategy" in d else None,
            linear=LinearSVM.from_dict(d["linear"]) if "linear" in d else None,
            kernel=KernelSVM.from_dict(d["kernel"]) if "kernel" in d else None,
        )


# ── NeuralNetwork ─────────────────────────────────────────────────────────────

@dataclass
class DenseLayer:
    """One fully connected layer of a NeuralNetwork."""

    weights: TensorValue = field(default_factory=TensorValue)
    bias: Optional[TensorValue] = None
    activation: NeuralNetworkActivation = NeuralNetworkActivation.ACTIVATION_UNSPECIFIED
    name: str = ""

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "DenseLayer":
        return cls(
            weights=TensorValue.from_dict(d.get("weights", {})),
            bias=TensorValue.from_dict(d["bias"]) if "bias" in d else None,
            activation=enum_from_dict(NeuralNetworkActivation, d.get("activation")),
            name=d.get("name", ""),
        )


@dataclass
class NeuralNetwork:
    """Structured classical feed-forward neural network body."""

    task_type: TaskType = TaskType.TASK_TYPE_UNSPECIFIED
    layers: list[DenseLayer] = field(default_factory=list)

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "NeuralNetwork":
        return cls(
            task_type=enum_from_dict(TaskType, d.get("task_type")),
            layers=[DenseLayer.from_dict(layer) for layer in d.get("layers", [])],
        )


# ── AnomalyDetection ──────────────────────────────────────────────────────────

@dataclass
class IsolationForest:
    trees: List[Tree] = field(default_factory=list)
    max_samples: int = 0
    offset: Optional[Scalar] = None

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "IsolationForest":
        return cls(
            trees=[Tree.from_dict(t) for t in d.get("trees", [])],
            max_samples=int_from_dict(d.get("max_samples")),
            offset=Scalar.from_dict(d["offset"]) if "offset" in d else None,
        )


@dataclass
class OneClassSVM:
    kernel_svm: Optional[KernelSVM] = None
    offset: Optional[Scalar] = None

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "OneClassSVM":
        return cls(
            kernel_svm=KernelSVM.from_dict(d["kernel_svm"]) if "kernel_svm" in d else None,
            offset=Scalar.from_dict(d["offset"]) if "offset" in d else None,
        )


@dataclass
class LinearOneClassSVM:
    coefficients: Optional[TensorValue] = None
    intercept: Optional[TensorValue] = None
    offset: Optional[Scalar] = None

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "LinearOneClassSVM":
        return cls(
            coefficients=TensorValue.from_dict(d["coefficients"]) if "coefficients" in d else None,
            intercept=TensorValue.from_dict(d["intercept"]) if "intercept" in d else None,
            offset=Scalar.from_dict(d["offset"]) if "offset" in d else None,
        )


@dataclass
class LocalOutlierFactor:
    reference_samples: Optional[TensorValue] = None
    n_neighbors: int = 0
    metric: str = "euclidean"
    metric_params: dict[str, str] = field(default_factory=dict)
    offset: Optional[Scalar] = None

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "LocalOutlierFactor":
        return cls(
            reference_samples=TensorValue.from_dict(d["reference_samples"])
                if "reference_samples" in d else None,
            n_neighbors=d.get("n_neighbors", 0),
            metric=d.get("metric", "euclidean"),
            metric_params=dict(d.get("metric_params", {})),
            offset=Scalar.from_dict(d["offset"]) if "offset" in d else None,
        )


@dataclass
class EllipticEnvelope:
    location: Optional[TensorValue] = None
    covariance: Optional[TensorValue] = None
    precision: Optional[TensorValue] = None
    offset: Optional[Scalar] = None

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "EllipticEnvelope":
        return cls(
            location=TensorValue.from_dict(d["location"]) if "location" in d else None,
            covariance=TensorValue.from_dict(d["covariance"]) if "covariance" in d else None,
            precision=TensorValue.from_dict(d["precision"]) if "precision" in d else None,
            offset=Scalar.from_dict(d["offset"]) if "offset" in d else None,
        )


@dataclass
class AnomalyDetection:
    """Structured anomaly detection model body."""

    task_type: TaskType = TaskType.ANOMALY_DETECTION
    mode: DetectionMode = DetectionMode.DETECTION_MODE_UNSPECIFIED
    raw_score_polarity: ScorePolarity = ScorePolarity.SCORE_POLARITY_UNSPECIFIED
    threshold: Optional[Scalar] = None
    isolation_forest: Optional[IsolationForest] = None
    one_class_svm: Optional[OneClassSVM] = None
    linear_one_class_svm: Optional[LinearOneClassSVM] = None
    local_outlier_factor: Optional[LocalOutlierFactor] = None
    elliptic_envelope: Optional[EllipticEnvelope] = None

    def to_dict(self) -> dict:
        return obj_to_dict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "AnomalyDetection":
        return cls(
            task_type=enum_from_dict(TaskType, d.get("task_type")),
            mode=enum_from_dict(DetectionMode, d.get("mode")),
            raw_score_polarity=enum_from_dict(ScorePolarity, d.get("raw_score_polarity")),
            threshold=Scalar.from_dict(d["threshold"]) if "threshold" in d else None,
            isolation_forest=IsolationForest.from_dict(d["isolation_forest"])
                if "isolation_forest" in d else None,
            one_class_svm=OneClassSVM.from_dict(d["one_class_svm"])
                if "one_class_svm" in d else None,
            linear_one_class_svm=LinearOneClassSVM.from_dict(d["linear_one_class_svm"])
                if "linear_one_class_svm" in d else None,
            local_outlier_factor=LocalOutlierFactor.from_dict(d["local_outlier_factor"])
                if "local_outlier_factor" in d else None,
            elliptic_envelope=EllipticEnvelope.from_dict(d["elliptic_envelope"])
                if "elliptic_envelope" in d else None,
        )
