"""OMLE IR — all public IR types re-exported from a single namespace."""

from .bodies import (
    SVM,
    AnomalyDetection,
    BernoulliNaiveBayes,
    CategoricalNaiveBayes,
    Clustering,
    ComplexPredicate,
    DenseLayer,
    EllipticEnvelope,
    GaussianMixtureClustering,
    GaussianNaiveBayes,
    IsolationForest,
    KernelSVM,
    Linear,
    LinearOneClassSVM,
    LinearSVM,
    LocalOutlierFactor,
    MultinomialNaiveBayes,
    NaiveBayes,
    NeuralNetwork,
    OneClassSVM,
    PrototypeClustering,
    Tree,
    TreeEnsemble,
)
from .domain import (
    ContinuousDomain,
    DiscreteDomain,
    DomainValue,
    Interval,
    ValueDomain,
)
from .enums import (
    BooleanOperator,
    CovarianceType,
    DataType,
    DetectionMode,
    DistanceMeasure,
    IntervalClosure,
    InvalidValuePolicy,
    MeasureLevel,
    MissingValuePolicy,
    NeuralNetworkActivation,
    OutlierValuePolicy,
    OutputRole,
    PostTransform,
    ScorePolarity,
    SimplePredicateOperator,
    SimpleSetOperator,
    SVMKernelType,
    SVMMulticlassStrategy,
    TargetKind,
    TaskType,
    TreeAggregation,
    TreeNodeKind,
    TreeSplitOp,
    ValueProperty,
)
from .expression import Apply, Expression
from .function import DefineFunction, FunctionParameter
from .interface import InputSpec, OutputBinding, OutputSpec
from .metadata import ModelMetadata, NamespaceImport, SourceFramework
from .model import OMLEModel
from .node import (
    Attribute,
    CompositeNode,
    NameAlias,
    Node,
    NodeInput,
    NodeOutput,
)
from .predicate import (
    CompoundPredicate,
    FalsePredicate,
    Predicate,
    SimplePredicate,
    SimpleSetPredicate,
    TruePredicate,
)
from .schema import Feature, ModelSchema, NameRange, Target
from .tensor import CSRMatrix, SparseTensor, Tensor, TensorEntry
from .types import NameRef, Scalar, TensorRef, TensorType, TensorValue
from .verification import (
    ModelVerification,
    NumericTolerance,
    RuntimeWarmup,
    SampleInputCase,
    SampleInputSet,
    VerificationCase,
    WarmupCase,
)

__all__ = [
    # enums
    "DataType", "MeasureLevel", "OutputRole", "PostTransform",
    "MissingValuePolicy", "InvalidValuePolicy", "OutlierValuePolicy",
    "TargetKind", "IntervalClosure", "ValueProperty",
    "SimplePredicateOperator", "SimpleSetOperator", "BooleanOperator",
    "TreeNodeKind", "TreeSplitOp", "TreeAggregation",
    "DistanceMeasure", "CovarianceType",
    "TaskType", "SVMKernelType", "SVMMulticlassStrategy", "NeuralNetworkActivation",
    "DetectionMode", "ScorePolarity",
    # core types
    "Scalar", "TensorType", "TensorRef", "TensorValue", "NameRef", "Tensor", "SparseTensor", "CSRMatrix", "TensorEntry",
    # metadata
    "ModelMetadata", "NamespaceImport", "SourceFramework",
    # interface
    "InputSpec", "OutputSpec", "OutputBinding",
    # domain
    "ValueDomain", "ContinuousDomain", "DiscreteDomain", "Interval", "DomainValue",
    # schema
    "ModelSchema", "Feature", "Target", "NameRange",
    # expression
    "Expression", "Apply",
    # predicate
    "Predicate", "TruePredicate", "FalsePredicate",
    "SimplePredicate", "SimpleSetPredicate", "CompoundPredicate",
    # node
    "Node", "NodeInput", "NodeOutput", "NameAlias", "CompositeNode", "Attribute",
    # function
    "DefineFunction", "FunctionParameter",
    # bodies
    "Linear",
    "NaiveBayes", "GaussianNaiveBayes", "MultinomialNaiveBayes",
    "BernoulliNaiveBayes", "CategoricalNaiveBayes",
    "Tree", "TreeEnsemble", "ComplexPredicate",
    "Clustering", "PrototypeClustering", "GaussianMixtureClustering",
    "LinearSVM", "KernelSVM", "SVM",
    "DenseLayer", "NeuralNetwork",
    "IsolationForest", "OneClassSVM", "LinearOneClassSVM",
    "LocalOutlierFactor", "EllipticEnvelope", "AnomalyDetection",
    # verification
    "NumericTolerance", "VerificationCase", "ModelVerification",
    "WarmupCase", "RuntimeWarmup",
    "SampleInputCase", "SampleInputSet",
    # model
    "OMLEModel",
]
