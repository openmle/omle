"""Bidirectional conversion between OMLE IR and protobuf messages.

This module requires:
  1. The ``protobuf`` package (``pip install protobuf``)
  2. A generated ``omle_pb2`` module in this directory.
     Run ``scripts/gen_proto.sh`` to generate it.
"""

from __future__ import annotations

import importlib
from typing import Any

from ..ir import bodies as _ir_bodies
from ..ir import domain as _ir_domain
from ..ir import expression as _ir_expr
from ..ir import function as _ir_func
from ..ir import interface as _ir_iface
from ..ir import metadata as _ir_meta
from ..ir import model as _ir_model
from ..ir import node as _ir_node
from ..ir import predicate as _ir_pred
from ..ir import schema as _ir_schema
from ..ir import tensor as _ir_tensor
from ..ir import types as _ir_types


def get_pb2():
    """Import and return the generated omle_pb2 module."""
    try:
        return importlib.import_module(".omle_pb2", package=__package__)
    except ImportError as exc:
        raise ImportError(
            "Could not import the generated omle_pb2 module. Make sure the "
            "'protobuf' package is installed (pip install protobuf). When working "
            "from a source checkout, run scripts/gen_proto.sh to generate it.\n"
            f"Original error: {exc}"
        ) from exc


# ── IR → Proto ────────────────────────────────────────────────────────────────

def ir_to_proto(model: _ir_model.OMLEModel) -> Any:
    pb2 = get_pb2()
    msg = pb2.OMLEModel()

    # metadata
    _copy_metadata(model.metadata, msg.metadata, pb2)

    # imports
    for ni in model.operator_imports:
        imp = msg.operator_imports.add()
        imp.namespace = ni.namespace
        imp.version = ni.version
    for ni in model.function_imports:
        imp = msg.function_imports.add()
        imp.namespace = ni.namespace
        imp.version = ni.version

    # inputs / outputs
    for spec in model.inputs:
        _copy_input_spec(spec, msg.inputs.add(), pb2)
    for spec in model.outputs:
        _copy_output_spec(spec, msg.outputs.add(), pb2)

    # schema
    if model.model_schema:
        _copy_model_schema(model.model_schema, msg.model_schema, pb2)

    # nodes
    for node in model.nodes:
        _copy_node(node, msg.nodes.add(), pb2)

    # tensor entries
    for t in model.tensor_entries:
        _copy_tensor_entry(t, msg.tensor_entries.add(), pb2)

    # functions
    for fn in model.functions:
        _copy_define_function(fn, msg.functions.add(), pb2)

    # verification / warmup / sample_inputs
    if model.verification:
        _copy_model_verification(model.verification, msg.verification, pb2)
    if model.warmup:
        _copy_runtime_warmup(model.warmup, msg.warmup, pb2)
    if model.sample_inputs:
        _copy_sample_input_set(model.sample_inputs, msg.sample_inputs, pb2)

    return msg


def ir_to_bytes(model: _ir_model.OMLEModel) -> bytes:
    """Serialize an OMLEModel IR directly to protobuf wire bytes."""
    return ir_to_proto(model).SerializeToString()


def _copy_metadata(meta: _ir_meta.ModelMetadata, msg: Any, pb2: Any) -> None:
    msg.format_version = meta.format_version
    msg.name = meta.name
    msg.version = meta.version
    msg.timestamp = meta.timestamp
    msg.producer = meta.producer
    msg.producer_version = meta.producer_version
    for sf in meta.source_frameworks:
        sf_msg = msg.source_frameworks.add()
        sf_msg.name = sf.name
        sf_msg.version = sf.version
        sf_msg.role = sf.role
    msg.doc_string = meta.doc_string
    if meta.copyright:
        msg.copyright = meta.copyright
    msg.attributes.update(meta.attributes)


def _copy_input_spec(spec: _ir_iface.InputSpec, msg: Any, pb2: Any) -> None:
    msg.name = spec.name
    if spec.type:
        _copy_tensor_type(spec.type, msg.type, pb2)
    msg.description = spec.description
    msg.attributes.update(spec.attributes)


def _copy_output_spec(spec: _ir_iface.OutputSpec, msg: Any, pb2: Any) -> None:
    msg.name = spec.name
    if spec.type:
        _copy_tensor_type(spec.type, msg.type, pb2)
    msg.role = spec.role.value
    if spec.binding:
        _copy_output_binding(spec.binding, msg.binding, pb2)
    msg.description = spec.description
    msg.field_names.extend(spec.field_names)
    msg.attributes.update(spec.attributes)


def _copy_output_binding(binding: _ir_iface.OutputBinding, msg: Any, pb2: Any) -> None:
    msg.target_name = binding.target_name
    for s in binding.values:
        _copy_scalar(s, msg.values.add())
    msg.segment_id = binding.segment_id
    msg.rank = binding.rank
    msg.attributes.update(binding.attributes)


def _copy_tensor_type(tt: _ir_types.TensorType, msg: Any, pb2: Any) -> None:
    msg.dtype = tt.dtype.value
    msg.shape.extend(tt.shape)


def _copy_scalar(scalar: _ir_types.Scalar, msg: Any) -> None:
    if scalar.bool_value is not None:
        msg.bool_value = scalar.bool_value
    elif scalar.int_value is not None:
        msg.int_value = scalar.int_value
    elif scalar.float_value is not None:
        msg.float_value = scalar.float_value
    elif scalar.double_value is not None:
        msg.double_value = scalar.double_value
    elif scalar.string_value is not None:
        msg.string_value = scalar.string_value


def _copy_tensor(t: _ir_tensor.Tensor, msg: Any, pb2: Any) -> None:
    msg.name = t.name
    if t.type:
        _copy_tensor_type(t.type, msg.type, pb2)
    # oneof data — set at most one branch
    if t.raw_data:
        msg.raw_data = t.raw_data
    elif t.float32_data:
        msg.float32_data.values.extend(t.float32_data)
    elif t.float64_data:
        msg.float64_data.values.extend(t.float64_data)
    elif t.int32_data:
        msg.int32_data.values.extend(t.int32_data)
    elif t.int64_data:
        msg.int64_data.values.extend(t.int64_data)
    elif t.string_data:
        msg.string_data.values.extend(t.string_data)
    elif t.bytes_data:
        msg.bytes_data.values.extend(t.bytes_data)
    elif t.bool_data:
        msg.bool_data.values.extend(t.bool_data)


def _copy_csr_matrix(csr: _ir_tensor.CSRMatrix, msg: Any, pb2: Any) -> None:
    msg.indices.extend(csr.indices)
    msg.indptr.extend(csr.indptr)
    if csr.raw_data:
        msg.raw_data = csr.raw_data
    elif csr.float32_data:
        msg.float32_data.values.extend(csr.float32_data)
    elif csr.float64_data:
        msg.float64_data.values.extend(csr.float64_data)
    elif csr.int32_data:
        msg.int32_data.values.extend(csr.int32_data)
    elif csr.int64_data:
        msg.int64_data.values.extend(csr.int64_data)
    elif csr.string_data:
        msg.string_data.values.extend(csr.string_data)


def _copy_sparse_tensor(st: _ir_tensor.SparseTensor, msg: Any, pb2: Any) -> None:
    msg.name = st.name
    if st.type:
        _copy_tensor_type(st.type, msg.type, pb2)
    if st.default_value is not None:
        _copy_scalar(st.default_value, msg.default_value)
    if st.csr is not None:
        _copy_csr_matrix(st.csr, msg.csr, pb2)
    msg.attributes.update(st.attributes)


def _copy_tensor_entry(entry: _ir_tensor.TensorEntry, msg: Any, pb2: Any) -> None:
    msg.id = entry.id
    if entry.dense is not None:
        _copy_tensor(entry.dense, msg.dense, pb2)
    elif entry.sparse is not None:
        _copy_sparse_tensor(entry.sparse, msg.sparse, pb2)
    msg.attributes.update(entry.attributes)


def _copy_model_schema(schema: _ir_schema.ModelSchema, msg: Any, pb2: Any) -> None:
    for f in schema.features:
        _copy_feature(f, msg.features.add(), pb2)
    for t in schema.targets:
        _copy_target(t, msg.targets.add(), pb2)


def _copy_feature(feat: _ir_schema.Feature, msg: Any, pb2: Any) -> None:
    if feat.name is not None:
        msg.name = feat.name
    elif feat.range is not None:
        _copy_name_range(feat.range, msg.range)
    msg.description = feat.description
    if feat.type:
        _copy_tensor_type(feat.type, msg.type, pb2)
    msg.measure_level = feat.measure_level.value
    msg.source = feat.source
    msg.index = feat.index
    msg.missing_value_policy = feat.missing_value_policy.value
    if feat.missing_replacement_value:
        _copy_scalar(feat.missing_replacement_value, msg.missing_replacement_value)
    msg.invalid_value_policy = feat.invalid_value_policy.value
    if feat.invalid_replacement_value:
        _copy_scalar(feat.invalid_replacement_value, msg.invalid_replacement_value)
    msg.outlier_value_policy = feat.outlier_value_policy.value
    if feat.domain:
        _copy_value_domain(feat.domain, msg.domain, pb2)
    msg.attributes.update(feat.attributes)


def _copy_name_range(nr: _ir_schema.NameRange, msg: Any) -> None:
    msg.prefix = nr.prefix
    msg.start = nr.start
    msg.end = nr.end
    msg.width = nr.width


def _copy_target(tgt: _ir_schema.Target, msg: Any, pb2: Any) -> None:
    msg.name = tgt.name
    if tgt.type:
        _copy_tensor_type(tgt.type, msg.type, pb2)
    msg.kind = tgt.kind.value
    msg.measure_level = tgt.measure_level.value
    for s in tgt.class_labels:
        _copy_scalar(s, msg.class_labels.add())
    msg.description = tgt.description
    msg.attributes.update(tgt.attributes)


def _copy_value_domain(domain: _ir_domain.ValueDomain, msg: Any, pb2: Any) -> None:
    if domain.continuous:
        for interval in domain.continuous.intervals:
            iv = msg.continuous.intervals.add()
            if interval.left_margin is not None:
                _copy_scalar(interval.left_margin, iv.left_margin)
            if interval.right_margin is not None:
                _copy_scalar(interval.right_margin, iv.right_margin)
            iv.closure = interval.closure.value
    if domain.discrete:
        for dv in domain.discrete.values:
            v = msg.discrete.values.add()
            if dv.value:
                _copy_scalar(dv.value, v.value)
            if dv.original_value:
                _copy_scalar(dv.original_value, v.original_value)
            v.display_name = dv.display_name
            v.property = dv.property.value
        msg.discrete.ordered = domain.discrete.ordered


def _copy_expression(expr: _ir_expr.Expression, msg: Any) -> None:
    if expr.literal is not None:
        _copy_scalar(expr.literal, msg.literal)
    elif expr.ref is not None:
        msg.ref.value = expr.ref
    elif expr.apply is not None:
        msg.apply.function = expr.apply.function
        for arg in expr.apply.arguments:
            _copy_expression(arg, msg.apply.arguments.add())


def _copy_predicate(pred: _ir_pred.Predicate, msg: Any) -> None:
    if pred.true_predicate is not None:
        msg.true_predicate.SetInParent()
    elif pred.false_predicate is not None:
        msg.false_predicate.SetInParent()
    elif pred.simple is not None:
        msg.simple.column.value = pred.simple.column
        msg.simple.op = pred.simple.op.value
        if pred.simple.value:
            _copy_scalar(pred.simple.value, msg.simple.value)
    elif pred.simple_set is not None:
        msg.simple_set.column.value = pred.simple_set.column
        msg.simple_set.op = pred.simple_set.op.value
        for s in pred.simple_set.values:
            _copy_scalar(s, msg.simple_set.values.add())
    elif pred.compound is not None:
        msg.compound.op = pred.compound.op.value
        for child in pred.compound.predicates:
            _copy_predicate(child, msg.compound.predicates.add())


def _copy_node(node: _ir_node.Node, msg: Any, pb2: Any) -> None:
    msg.name = node.name
    msg.domain = node.domain
    msg.op = node.op
    for inp in node.inputs:
        ni = msg.inputs.add()
        if inp.name is not None:
            ni.name.value = inp.name.value
            if inp.name.field:
                ni.name.field = inp.name.field
        elif inp.range is not None:
            _copy_name_range(inp.range, ni.range)
    for out in node.outputs:
        no = msg.outputs.add()
        no.name = out.name
        if out.type:
            _copy_tensor_type(out.type, no.type, pb2)
        no.measure_level = out.measure_level.value
        if out.domain:
            _copy_value_domain(out.domain, no.domain, pb2)
        no.description = out.description
        no.role = out.role.value
        if out.binding:
            _copy_output_binding(out.binding, no.binding, pb2)
        no.field_names.extend(out.field_names)
        no.attributes.update(out.attributes)
    for attr in node.attributes:
        _copy_attribute(attr, msg.attributes.add(), pb2)
    msg.metadata.update(node.metadata)

    # body
    if node.linear is not None:
        msg.linear.task_type = node.linear.task_type.value
        _copy_tensor_value(node.linear.coefficients, msg.linear.coefficients, pb2)
        _copy_tensor_value(node.linear.intercept, msg.linear.intercept, pb2)
        _copy_tensor_value(node.linear.weight_covariances, msg.linear.weight_covariances, pb2)
        _copy_tensor_value(node.linear.noise_precision, msg.linear.noise_precision, pb2)
        msg.linear.post_transform = node.linear.post_transform.value
    elif node.tree_ensemble is not None:
        _copy_tree_ensemble(node.tree_ensemble, msg.tree_ensemble, pb2)
    elif node.tree is not None:
        _copy_tree(node.tree, msg.tree, pb2)
    elif node.naive_bayes is not None:
        _copy_naive_bayes(node.naive_bayes, msg.naive_bayes, pb2)
    elif node.clustering is not None:
        _copy_clustering(node.clustering, msg.clustering, pb2)
    elif node.svm is not None:
        _copy_svm(node.svm, msg.svm, pb2)
    elif node.neural_network is not None:
        _copy_neural_network(node.neural_network, msg.neural_network, pb2)
    elif node.anomaly_detection is not None:
        _copy_anomaly_detection(node.anomaly_detection, msg.anomaly_detection, pb2)
    elif node.composite is not None:
        _copy_composite(node.composite, msg.composite, pb2)


def _copy_attribute(attr: _ir_node.Attribute, msg: Any, pb2: Any = None) -> None:
    msg.name = attr.name
    if attr.i is not None:
        msg.i = attr.i
    elif attr.f32 is not None:
        msg.f32 = attr.f32
    elif attr.f64 is not None:
        msg.f64 = attr.f64
    elif attr.s is not None:
        msg.s = attr.s
    elif attr.b is not None:
        msg.b = attr.b
    elif attr.ints is not None:
        msg.ints.values.extend(attr.ints)
    elif attr.float32s is not None:
        msg.float32s.values.extend(attr.float32s)
    elif attr.float64s is not None:
        msg.float64s.values.extend(attr.float64s)
    elif attr.strings is not None:
        msg.strings.values.extend(attr.strings)
    elif attr.bools is not None:
        msg.bools.values.extend(attr.bools)
    elif attr.tensor_ref is not None:
        msg.tensor_ref.id = attr.tensor_ref.id
    elif attr.tensor is not None and pb2 is not None:
        _copy_tensor(attr.tensor, msg.tensor, pb2)
    elif attr.sparse is not None and pb2 is not None:
        _copy_sparse_tensor(attr.sparse, msg.sparse, pb2)
    elif attr.type is not None:
        pass  # TensorType attribute — skip deep copy for brevity
    elif attr.expr is not None:
        _copy_expression(attr.expr, msg.expr)
    elif attr.predicate is not None:
        _copy_predicate(attr.predicate, msg.predicate)


def _copy_tree(tree: _ir_bodies.Tree, msg: Any, pb2: Any) -> None:
    msg.task_type = tree.task_type.value
    msg.num_nodes = tree.num_nodes
    msg.node_kind.extend(k.value for k in tree.node_kind)
    msg.split_feature.extend(tree.split_feature)
    _copy_tensor_value(tree.split_threshold, msg.split_threshold, pb2)
    msg.split_op.extend(op.value for op in tree.split_op)
    msg.category_set_offset.extend(tree.category_set_offset)
    msg.category_set_count.extend(tree.category_set_count)
    msg.category_set.extend(tree.category_set)
    for cp in tree.complex_predicates:
        cpb = msg.complex_predicates.add()
        cpb.node_index = cp.node_index
        if cp.predicate:
            _copy_predicate(cp.predicate, cpb.predicate)
    msg.children_index.extend(tree.children_index)
    msg.children_offset.extend(tree.children_offset)
    msg.children_count.extend(tree.children_count)
    msg.default_child.extend(tree.default_child)
    _copy_tensor_value(tree.leaf_value, msg.leaf_value, pb2)
    msg.leaf_width = tree.leaf_width
    _copy_tensor_value(tree.leaf_vector, msg.leaf_vector, pb2)
    msg.leaf_vector_index.extend(tree.leaf_vector_index)


def _copy_tree_ensemble(te: _ir_bodies.TreeEnsemble, msg: Any, pb2: Any) -> None:
    msg.task_type = te.task_type.value
    for tree in te.trees:
        _copy_tree(tree, msg.trees.add(), pb2)
    msg.aggregation = te.aggregation.value
    msg.post_transform = te.post_transform.value
    _copy_tensor_value(te.tree_weights, msg.tree_weights, pb2)
    _copy_tensor_value(te.base_scores, msg.base_scores, pb2)
    msg.tree_group.extend(te.tree_group)


def _copy_naive_bayes(nb: _ir_bodies.NaiveBayes, msg: Any, pb2: Any) -> None:
    msg.task_type = nb.task_type.value
    _copy_tensor_value(nb.class_log_priors, msg.class_log_priors, pb2)
    if nb.gaussian:
        _copy_tensor_value(nb.gaussian.means, msg.gaussian.means, pb2)
        _copy_tensor_value(nb.gaussian.variances, msg.gaussian.variances, pb2)
        if nb.gaussian.variance_epsilon is not None:
            _copy_scalar(nb.gaussian.variance_epsilon, msg.gaussian.variance_epsilon)
    elif nb.multinomial:
        _copy_tensor_value(nb.multinomial.feature_log_prob, msg.multinomial.feature_log_prob, pb2)
    elif nb.bernoulli:
        _copy_tensor_value(nb.bernoulli.feature_log_prob, msg.bernoulli.feature_log_prob, pb2)
        if nb.bernoulli.binarize_threshold is not None:
            _copy_scalar(nb.bernoulli.binarize_threshold, msg.bernoulli.binarize_threshold)
    elif nb.categorical:
        _copy_tensor_value(nb.categorical.category_log_prob, msg.categorical.category_log_prob, pb2)
        msg.categorical.category_offset.extend(nb.categorical.category_offset)
        msg.categorical.category_count.extend(nb.categorical.category_count)


def _copy_clustering(cl: _ir_bodies.Clustering, msg: Any, pb2: Any) -> None:
    msg.task_type = cl.task_type.value
    if cl.prototype:
        _copy_tensor_value(cl.prototype.centers, msg.prototype.centers, pb2)
        msg.prototype.distance_measure = cl.prototype.distance_measure.value
        for lbl in cl.prototype.cluster_labels:
            _copy_scalar(lbl, msg.prototype.cluster_labels.add())
    elif cl.gaussian_mixture:
        gm = cl.gaussian_mixture
        _copy_tensor_value(gm.weights, msg.gaussian_mixture.weights, pb2)
        _copy_tensor_value(gm.means, msg.gaussian_mixture.means, pb2)
        _copy_tensor_value(gm.covariances, msg.gaussian_mixture.covariances, pb2)
        msg.gaussian_mixture.covariance_type = gm.covariance_type.value
        for lbl in gm.component_labels:
            _copy_scalar(lbl, msg.gaussian_mixture.component_labels.add())


def _copy_svm(svm: _ir_bodies.SVM, msg: Any, pb2: Any) -> None:
    msg.task_type = svm.task_type.value
    msg.post_transform = svm.post_transform.value
    if svm.multiclass_strategy is not None:
        msg.multiclass_strategy = svm.multiclass_strategy.value
    if svm.linear is not None:
        _copy_tensor_value(svm.linear.coefficients, msg.linear.coefficients, pb2)
        _copy_tensor_value(svm.linear.intercept, msg.linear.intercept, pb2)
    elif svm.kernel is not None:
        k = svm.kernel
        msg.kernel.kernel_type = k.kernel_type.value
        _copy_tensor_value(k.support_vectors, msg.kernel.support_vectors, pb2)
        _copy_tensor_value(k.dual_coefficients, msg.kernel.dual_coefficients, pb2)
        _copy_tensor_value(k.intercept, msg.kernel.intercept, pb2)
        if k.gamma is not None:
            _copy_scalar(k.gamma, msg.kernel.gamma)
        if k.degree is not None:
            msg.kernel.degree = k.degree
        if k.coef0 is not None:
            _copy_scalar(k.coef0, msg.kernel.coef0)
        msg.kernel.n_support.extend(k.n_support)
        _copy_tensor_value(k.prob_a, msg.kernel.prob_a, pb2)
        _copy_tensor_value(k.prob_b, msg.kernel.prob_b, pb2)


def _copy_neural_network(nn: _ir_bodies.NeuralNetwork, msg: Any, pb2: Any) -> None:
    msg.task_type = nn.task_type.value
    for layer in nn.layers:
        lm = msg.layers.add()
        _copy_tensor_value(layer.weights, lm.weights, pb2)
        _copy_tensor_value(layer.bias, lm.bias, pb2)
        lm.activation = layer.activation.value
        lm.name = layer.name


def _copy_anomaly_detection(ad: _ir_bodies.AnomalyDetection, msg: Any, pb2: Any) -> None:
    msg.task_type = ad.task_type.value
    msg.mode = ad.mode.value
    msg.raw_score_polarity = ad.raw_score_polarity.value
    if ad.threshold is not None:
        _copy_scalar(ad.threshold, msg.threshold)
    if ad.isolation_forest is not None:
        for t in ad.isolation_forest.trees:
            _copy_tree(t, msg.isolation_forest.trees.add(), pb2)
        msg.isolation_forest.max_samples = ad.isolation_forest.max_samples
        if ad.isolation_forest.offset is not None:
            _copy_scalar(ad.isolation_forest.offset, msg.isolation_forest.offset)
    elif ad.one_class_svm is not None:
        if ad.one_class_svm.kernel_svm is not None:
            k = ad.one_class_svm.kernel_svm
            km = msg.one_class_svm.kernel_svm
            km.kernel_type = k.kernel_type.value
            _copy_tensor_value(k.support_vectors, km.support_vectors, pb2)
            _copy_tensor_value(k.dual_coefficients, km.dual_coefficients, pb2)
            _copy_tensor_value(k.intercept, km.intercept, pb2)
            if k.gamma is not None:
                _copy_scalar(k.gamma, km.gamma)
            if k.degree is not None:
                km.degree = k.degree
            if k.coef0 is not None:
                _copy_scalar(k.coef0, km.coef0)
            km.n_support.extend(k.n_support)
        if ad.one_class_svm.offset is not None:
            _copy_scalar(ad.one_class_svm.offset, msg.one_class_svm.offset)
    elif ad.linear_one_class_svm is not None:
        lo = ad.linear_one_class_svm
        _copy_tensor_value(lo.coefficients, msg.linear_one_class_svm.coefficients, pb2)
        _copy_tensor_value(lo.intercept, msg.linear_one_class_svm.intercept, pb2)
        if lo.offset is not None:
            _copy_scalar(lo.offset, msg.linear_one_class_svm.offset)
    elif ad.local_outlier_factor is not None:
        lof = ad.local_outlier_factor
        _copy_tensor_value(lof.reference_samples, msg.local_outlier_factor.reference_samples, pb2)
        msg.local_outlier_factor.n_neighbors = lof.n_neighbors
        msg.local_outlier_factor.metric = lof.metric
        msg.local_outlier_factor.metric_params.update(lof.metric_params)
        if lof.offset is not None:
            _copy_scalar(lof.offset, msg.local_outlier_factor.offset)
    elif ad.elliptic_envelope is not None:
        ee = ad.elliptic_envelope
        _copy_tensor_value(ee.location, msg.elliptic_envelope.location, pb2)
        _copy_tensor_value(ee.covariance, msg.elliptic_envelope.covariance, pb2)
        _copy_tensor_value(ee.precision, msg.elliptic_envelope.precision, pb2)
        if ee.offset is not None:
            _copy_scalar(ee.offset, msg.elliptic_envelope.offset)


def _copy_composite(comp: _ir_node.CompositeNode, msg: Any, pb2: Any) -> None:
    for alias in comp.input_aliases:
        a = msg.input_aliases.add()
        a.from_name = alias.from_name
        a.to_name = alias.to_name
    for node in comp.nodes:
        _copy_node(node, msg.nodes.add(), pb2)
    for alias in comp.output_aliases:
        a = msg.output_aliases.add()
        a.from_name = alias.from_name
        a.to_name = alias.to_name


def _copy_tensor_ref(tr: _ir_types.TensorRef, msg: Any) -> None:
    msg.id = tr.id


def _copy_tensor_value(ir_tv: "_ir_types.TensorValue | None", pb2_field: Any, pb2: Any) -> None:
    """Copy a TensorValue IR object into a proto TensorValue message field."""
    if ir_tv is None:
        return
    if ir_tv.tensor is not None:
        _copy_tensor(ir_tv.tensor, pb2_field.tensor, pb2)
    elif ir_tv.sparse is not None:
        _copy_sparse_tensor(ir_tv.sparse, pb2_field.sparse, pb2)
    elif ir_tv.tensor_ref is not None:
        pb2_field.tensor_ref.id = ir_tv.tensor_ref.id


def _copy_model_verification(v: Any, msg: Any, pb2: Any) -> None:
    for case in v.cases:
        cm = msg.cases.add()
        for ref in case.inputs:
            _copy_tensor_ref(ref, cm.inputs.add())
        for ref in case.expected_outputs:
            _copy_tensor_ref(ref, cm.expected_outputs.add())
        cm.description = case.description
    if v.tolerance is not None:
        if v.tolerance.atol is not None:
            _copy_scalar(v.tolerance.atol, msg.tolerance.atol)
        if v.tolerance.rtol is not None:
            _copy_scalar(v.tolerance.rtol, msg.tolerance.rtol)


def _copy_runtime_warmup(w: Any, msg: Any, pb2: Any) -> None:
    for case in w.cases:
        cm = msg.cases.add()
        for ref in case.inputs:
            _copy_tensor_ref(ref, cm.inputs.add())
        cm.description = case.description
        cm.repeat = case.repeat


def _copy_sample_input_set(s: Any, msg: Any, pb2: Any) -> None:
    for case in s.cases:
        cm = msg.cases.add()
        for ref in case.inputs:
            _copy_tensor_ref(ref, cm.inputs.add())
        cm.description = case.description


def _copy_define_function(fn: _ir_func.DefineFunction, msg: Any, pb2: Any) -> None:
    msg.name = fn.name
    msg.doc_string = fn.doc_string
    for p in fn.parameters:
        pm = msg.parameters.add()
        pm.name = p.name
        pm.data_type = p.data_type.value
        pm.measure_level = p.measure_level.value
    msg.result_data_type = fn.result_data_type.value
    msg.result_measure_level = fn.result_measure_level.value
    if fn.body:
        _copy_expression(fn.body, msg.body)
    msg.attributes.update(fn.attributes)


# ── Proto → IR ────────────────────────────────────────────────────────────────

def proto_to_ir(msg: Any) -> _ir_model.OMLEModel:
    """Convert a protobuf OMLEModel message to the IR representation."""
    from ..ir import (
        OMLEModel,
        Scalar,
        TensorRef,
        TensorType,
        enums,
    )

    def scalar(s) -> Scalar:
        field = s.WhichOneof("value")
        if field == "bool_value":
            return Scalar(bool_value=s.bool_value)
        if field == "int_value":
            return Scalar(int_value=s.int_value)
        if field == "float_value":
            return Scalar(float_value=s.float_value)
        if field == "double_value":
            return Scalar(double_value=s.double_value)
        if field == "string_value":
            return Scalar(string_value=s.string_value)
        return Scalar()

    def tensor_type(tt) -> TensorType:
        return TensorType(dtype=enums.DataType(tt.dtype), shape=list(tt.shape))

    def tensor_ref(tr) -> TensorRef:
        return TensorRef(id=tr.id)

    # The full proto→IR conversion is symmetric to IR→proto above.
    # For brevity we delegate to the JSON round-trip using MessageToJson.
    import json

    from google.protobuf import json_format
    d = json.loads(json_format.MessageToJson(msg, preserving_proto_field_name=True,
                                              always_print_fields_with_no_presence=False))
    return OMLEModel.from_dict(d)
