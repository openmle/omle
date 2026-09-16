"""All enum types from the OMLE v1 protobuf schema."""

from enum import Enum


class DataType(Enum):
    DATA_TYPE_UNSPECIFIED = 0
    BOOL = 1
    INT8 = 2
    INT16 = 3
    INT32 = 4
    INT64 = 5
    UINT8 = 6
    UINT16 = 7
    UINT32 = 8
    UINT64 = 9
    FLOAT16 = 10
    FLOAT32 = 11
    FLOAT64 = 12
    STRING = 13
    BYTES = 14
    DATE = 15
    TIME = 16
    TIMESTAMP = 17


class MeasureLevel(Enum):
    MEASURE_LEVEL_UNSPECIFIED = 0
    CONTINUOUS = 1
    NOMINAL = 2
    ORDINAL = 3
    FLAG = 4


class OutputRole(Enum):
    OUTPUT_ROLE_UNSPECIFIED = 0
    PREDICTION = 1
    PROBABILITY = 2
    SCORE = 3
    CONFIDENCE = 4
    STANDARD_ERROR = 5
    STANDARD_DEVIATION = 6
    RESIDUAL = 7
    TRANSFORMED_VALUE = 8
    ENTITY_ID = 9
    AFFINITY = 10
    CONTRIBUTION = 11
    INTERMEDIATE = 12


class PostTransform(Enum):
    POST_TRANSFORM_UNSPECIFIED = 0
    IDENTITY = 1
    SIGMOID = 2
    SIGMOID_BINARY = 3
    SOFTMAX = 4
    LOGIT = 5
    PROBIT = 6
    EXP = 7
    CLOGLOG = 8
    CAUCHIT = 9
    LOGLOG = 10


class MissingValuePolicy(Enum):
    MISSING_PROPAGATE = 0
    MISSING_AS_VALUE = 1
    MISSING_AS_INVALID = 2


class InvalidValuePolicy(Enum):
    INVALID_RETURN_INVALID = 0
    INVALID_AS_IS = 1
    INVALID_AS_MISSING = 2
    INVALID_AS_VALUE = 3


class OutlierValuePolicy(Enum):
    OUTLIER_AS_IS = 0
    OUTLIER_AS_MISSING = 1
    OUTLIER_AS_EXTREME = 2


class TargetKind(Enum):
    TARGET_KIND_UNSPECIFIED = 0
    REGRESSION = 1
    BINARY = 2
    MULTICLASS = 3


class IntervalClosure(Enum):
    CLOSURE_UNSPECIFIED = 0
    OPEN_OPEN = 1
    OPEN_CLOSED = 2
    CLOSED_OPEN = 3
    CLOSED_CLOSED = 4


class ValueProperty(Enum):
    VALID = 0
    INVALID = 1
    MISSING = 2


class SimplePredicateOperator(Enum):
    OPERATOR_UNSPECIFIED = 0
    LESS_THAN = 1
    LESS_OR_EQUAL = 2
    GREATER_THAN = 3
    GREATER_OR_EQUAL = 4
    EQUAL = 5
    NOT_EQUAL = 6
    IS_MISSING = 7
    IS_NOT_MISSING = 8


class SimpleSetOperator(Enum):
    OPERATOR_UNSPECIFIED = 0
    IN = 1
    NOT_IN = 2


class BooleanOperator(Enum):
    BOOLEAN_OPERATOR_UNSPECIFIED = 0
    AND = 1
    OR = 2
    XOR = 3
    SURROGATE = 4


class TreeNodeKind(Enum):
    NODE_KIND_UNSPECIFIED = 0
    LEAF = 1
    BRANCH = 2


class TreeSplitOp(Enum):
    SPLIT_OP_UNSPECIFIED = 0
    LESS_THAN = 1
    LESS_OR_EQUAL = 2
    GREATER_THAN = 3
    GREATER_OR_EQUAL = 4
    EQUAL = 5
    NOT_EQUAL = 6
    IN_SET = 7
    NOT_IN_SET = 8
    IS_MISSING = 9


class TreeAggregation(Enum):
    AGGREGATION_UNSPECIFIED = 0
    SUM = 1
    AVERAGE = 2
    WEIGHTED_SUM = 3
    WEIGHTED_AVERAGE = 4
    MAJORITY_VOTE = 5
    SOFT_VOTE = 6
    MIN = 7
    MAX = 8




class DistanceMeasure(Enum):
    DISTANCE_MEASURE_UNSPECIFIED = 0
    EUCLIDEAN = 1
    SQUARED_EUCLIDEAN = 2
    MANHATTAN = 3
    COSINE = 4


class CovarianceType(Enum):
    COVARIANCE_TYPE_UNSPECIFIED = 0
    FULL = 1
    DIAGONAL = 2
    SPHERICAL = 3


class TaskType(Enum):
    TASK_TYPE_UNSPECIFIED = 0
    REGRESSION = 1
    BINARY = 2
    MULTICLASS = 3
    CLUSTERING = 4
    ANOMALY_DETECTION = 5


class SVMMulticlassStrategy(Enum):
    MULTICLASS_STRATEGY_UNSPECIFIED = 0
    ONE_VS_REST = 1
    ONE_VS_ONE = 2


class SVMKernelType(Enum):
    KERNEL_TYPE_UNSPECIFIED = 0
    LINEAR = 1
    POLY = 2
    RBF = 3
    SIGMOID = 4


class NeuralNetworkActivation(Enum):
    ACTIVATION_UNSPECIFIED = 0
    IDENTITY = 1
    LOGISTIC = 2
    TANH = 3
    RELU = 4
    SOFTMAX = 5


class DetectionMode(Enum):
    DETECTION_MODE_UNSPECIFIED = 0
    OUTLIER_DETECTION = 1
    NOVELTY_DETECTION = 2


class ScorePolarity(Enum):
    SCORE_POLARITY_UNSPECIFIED = 0
    HIGHER_MORE_ABNORMAL = 1
    LOWER_MORE_ABNORMAL = 2
