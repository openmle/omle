"""OMLE model validator.

Structural rules (always checked):
  - Name uniqueness (inputs, features, node outputs, tensor entries, functions)
  - OutputSpec.name resolves to an input or node output
  - NameRange validity (start >= 0, end >= start, width >= 0)
  - Feature source references a declared InputSpec
  - No duplicate function names; no recursive function calls
  - No cycles in the node graph (DAG check)
  - Probability output binding alignment
  - (role, binding) uniqueness per node
  - verification: TensorRef ids resolve to tensor_entries; inner tensor names
    match model inputs/outputs; tolerance atol/rtol >= 0
  - warmup: TensorRef ids resolve; repeat not negative
  - sample_inputs: TensorRef ids resolve; inner tensor names match model inputs

Registry rules (checked when registries are available):
  - Node domain+op exists in the imported namespace
  - Namespace is declared in operator_imports when domain is a standard namespace
  - Required node attributes are present
  - Enum-constrained attributes hold a valid value
  - Structured operators have the correct body field set
  - Split: num outputs == len(sections), all sections > 0
  - Impute: exactly one of fill_value or fill_tensor is present
  - OneHotEncode: K == len(categories) if output shape is declared
  - Apply.function names resolve against imported function namespaces
  - Apply argument count falls within the function's declared arity
  - map_values: pairs argument count is even
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .ir.enums import OutputRole, TargetKind
from .ir.expression import Apply, Expression
from .ir.function import DefineFunction
from .ir.model import OMLEModel
from .ir.node import Node
from .ir.schema import NameRange
from .ir.types import Scalar


@dataclass
class ValidationError:
    path: str
    message: str

    def __str__(self) -> str:
        return f"[{self.path}] {self.message}"


@dataclass
class ValidationResult:
    errors: list[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def error(self, path: str, msg: str) -> None:
        self.errors.append(ValidationError(path, msg))

    def __str__(self) -> str:
        if self.is_valid:
            return "Valid"
        lines = [f"  {e}" for e in self.errors]
        return "Validation failed:\n" + "\n".join(lines)


class ModelValidator:
    """Validates an OMLEModel against OMLE v1 rules."""

    def validate(self, model: OMLEModel, *,
                 use_registry: bool = True) -> ValidationResult:
        """Validate a model.

        Args:
            model: The model to validate.
            use_registry: When True (default) load the operator and function
                registries and run additional registry-aware checks. Pass
                False to skip registry checks (e.g. in offline environments
                where the registry files may not be present).
        """
        result = ValidationResult()
        self._check_metadata(model, result)
        self._check_inputs(model, result)
        self._check_name_ranges(model, result)
        self._check_features(model, result)
        self._check_outputs(model, result)
        self._check_nodes(model, result)
        self._check_tensor_entries(model, result)
        self._check_functions(model, result)
        self._check_verification(model, result)
        self._check_warmup(model, result)
        self._check_sample_inputs(model, result)

        if use_registry:
            try:
                from .registry import (
                    get_function_registry,
                    get_operator_registry,
                )
                op_reg = get_operator_registry()
                fn_reg = get_function_registry()
            except FileNotFoundError:
                result.error(
                    "registry",
                    "Registry files not found — skipping registry-based checks. "
                    "Pass use_registry=False to suppress this warning.",
                )
            else:
                imported_fn_ns = [imp.namespace for imp in model.function_imports]
                self._check_operator_imports(model, op_reg, result)
                tensor_entry_map = {e.id: e for e in model.tensor_entries if e.id}
                for i, node in enumerate(model.nodes):
                    self._check_node_registry(node, i, op_reg, result, tensor_entry_map)
                self._check_expressions_registry(model, fn_reg, imported_fn_ns, result)

        return result

    # ── metadata ──────────────────────────────────────────────────────────────

    def _check_metadata(self, model: OMLEModel, r: ValidationResult) -> None:
        if not model.metadata.format_version:
            r.error("metadata.format_version", "format_version must not be empty")

    # ── inputs ────────────────────────────────────────────────────────────────

    def _check_inputs(self, model: OMLEModel, r: ValidationResult) -> None:
        seen: set[str] = set()
        for i, spec in enumerate(model.inputs):
            if not spec.name:
                r.error(f"inputs[{i}].name", "Input name must not be empty")
                continue
            if spec.name in seen:
                r.error(f"inputs[{i}].name", f"Duplicate input name: {spec.name!r}")
            seen.add(spec.name)

    # ── name ranges ───────────────────────────────────────────────────────────

    def _check_name_range(self, nr: NameRange, path: str, r: ValidationResult) -> None:
        if nr.start < 0:
            r.error(path, f"NameRange.start must be >= 0, got {nr.start}")
        if nr.end < nr.start:
            r.error(path, f"NameRange.end ({nr.end}) must be >= start ({nr.start})")
        if nr.width < 0:
            r.error(path, f"NameRange.width must be >= 0, got {nr.width}")

    def _check_name_ranges(self, model: OMLEModel, r: ValidationResult) -> None:
        if model.model_schema:
            for i, feat in enumerate(model.model_schema.features):
                if feat.range is not None:
                    self._check_name_range(
                        feat.range, f"model_schema.features[{i}].range", r
                    )
        for i, node in enumerate(model.nodes):
            for j, inp in enumerate(node.inputs):
                if inp.range is not None:
                    self._check_name_range(
                        inp.range, f"nodes[{i}].inputs[{j}].range", r
                    )

    # ── features ──────────────────────────────────────────────────────────────

    def _check_features(self, model: OMLEModel, r: ValidationResult) -> None:
        if not model.model_schema:
            return
        input_names = {spec.name for spec in model.inputs}
        seen_feature_names: set[str] = set()

        for i, feat in enumerate(model.model_schema.features):
            expanded = feat.expand_names()
            if not expanded:
                r.error(f"model_schema.features[{i}]", "Feature has no name or range set")
                continue

            for nm in expanded:
                if nm in seen_feature_names:
                    r.error(f"model_schema.features[{i}]",
                            f"Duplicate feature name: {nm!r}")
                seen_feature_names.add(nm)

            if feat.source and feat.source not in input_names:
                r.error(f"model_schema.features[{i}].source",
                        f"Source {feat.source!r} does not match any InputSpec name")

    # ── outputs ───────────────────────────────────────────────────────────────

    def _check_outputs(self, model: OMLEModel, r: ValidationResult) -> None:
        resolvable: set[str] = {spec.name for spec in model.inputs}
        for node in model.nodes:
            for out in node.outputs:
                resolvable.add(out.name)

        target_map = {}
        if model.model_schema:
            for tgt in model.model_schema.targets:
                target_map[tgt.name] = tgt

        seen_output_names: set[str] = set()
        for i, spec in enumerate(model.outputs):
            if not spec.name:
                r.error(f"outputs[{i}].name", "Output name must not be empty")
                continue
            if spec.name in seen_output_names:
                r.error(f"outputs[{i}].name", f"Duplicate output name: {spec.name!r}")
            seen_output_names.add(spec.name)

            if spec.name not in resolvable:
                r.error(f"outputs[{i}].name",
                        f"Output name {spec.name!r} does not resolve to any input "
                        "or node output")

            # Probability binding check
            if spec.role == OutputRole.PROBABILITY and spec.binding:
                tgt_name = spec.binding.target_name
                if tgt_name and tgt_name in target_map:
                    tgt = target_map[tgt_name]
                    n_classes = len(tgt.class_labels)
                    n_bound_vals = len(spec.binding.values)
                    if tgt.kind in (TargetKind.BINARY, TargetKind.MULTICLASS):
                        if n_bound_vals > 1 and spec.type and spec.type.shape:
                            last_dim = spec.type.shape[-1]
                            if last_dim != n_classes:
                                r.error(
                                    f"outputs[{i}]",
                                    f"PROBABILITY output last dimension ({last_dim}) "
                                    f"must equal number of class labels ({n_classes}) "
                                    f"for target {tgt_name!r}",
                                )

    # ── nodes ─────────────────────────────────────────────────────────────────

    def _check_nodes(self, model: OMLEModel, r: ValidationResult) -> None:
        seen_node_names: set[str] = set()
        for i, node in enumerate(model.nodes):
            if not node.name:
                r.error(f"nodes[{i}].name", "Node name must not be empty")
            elif node.name in seen_node_names:
                r.error(f"nodes[{i}].name", f"Duplicate node name: {node.name!r}")
            seen_node_names.add(node.name)

            self._check_node_outputs_unique(node, i, r)

        self._check_dag(model.nodes, r)

    def _check_node_outputs_unique(self, node: Node, node_idx: int,
                                    r: ValidationResult) -> None:
        seen_names: set[str] = set()
        seen_role_binding: set[tuple] = set()

        for j, out in enumerate(node.outputs):
            path = f"nodes[{node_idx}].outputs[{j}]"
            if not out.name:
                r.error(path + ".name", "NodeOutput name must not be empty")
                continue
            if out.name in seen_names:
                r.error(path + ".name",
                        f"Duplicate NodeOutput name {out.name!r} in node {node.name!r}")
            seen_names.add(out.name)

            # Only enforce (role, binding) uniqueness when a semantic role is set.
            # Outputs with unspecified roles (e.g. intermediate Split outputs) are
            # distinguished solely by name, not by role/binding.
            if out.role != OutputRole.OUTPUT_ROLE_UNSPECIFIED:
                binding_key = (
                    out.role.name,
                    out.binding.target_name if out.binding else "",
                    tuple(v.value for v in out.binding.values) if out.binding else (),
                )
                if binding_key in seen_role_binding:
                    r.error(path, f"Duplicate (role, binding) pair in node {node.name!r}")
                seen_role_binding.add(binding_key)

    def _check_dag(self, nodes: list[Node], r: ValidationResult) -> None:
        """Verify the top-level node graph is a DAG (no cycles)."""
        # Build dependency edges based on input/output names
        produces: dict[str, str] = {}  # output_name -> node_name
        for node in nodes:
            for out in node.outputs:
                if out.name:
                    produces[out.name] = node.name

        deps: dict[str, set[str]] = {node.name: set() for node in nodes}
        for node in nodes:
            for inp in node.inputs:
                if inp.name and inp.name in produces:
                    deps[node.name].add(produces[inp.name])

        # Topological sort (Kahn's algorithm)
        from collections import deque
        in_degree: dict[str, int] = {n: 0 for n in deps}
        for node_deps in deps.values():
            for dep in node_deps:
                if dep in in_degree:
                    in_degree[dep] += 1

        # Reverse: we need successors
        successors: dict[str, list[str]] = {n: [] for n in deps}
        for node_name, node_deps in deps.items():
            for dep in node_deps:
                if dep in successors:
                    successors[dep].append(node_name)

        in_degree_fwd: dict[str, int] = {n: 0 for n in deps}
        for node_name, node_deps in deps.items():
            in_degree_fwd[node_name] = len(node_deps)

        queue: deque[str] = deque(n for n, d in in_degree_fwd.items() if d == 0)
        processed = 0
        while queue:
            node_name = queue.popleft()
            processed += 1
            for succ in successors.get(node_name, []):
                in_degree_fwd[succ] -= 1
                if in_degree_fwd[succ] == 0:
                    queue.append(succ)

        if processed < len(deps):
            cycle_nodes = [n for n, d in in_degree_fwd.items() if d > 0]
            r.error("nodes", f"Graph contains a cycle involving nodes: {cycle_nodes}")

    # ── tensor entries ─────────────────────────────────────────────────────────

    def _check_tensor_entries(self, model: OMLEModel, r: ValidationResult) -> None:
        seen: set[str] = set()
        for i, entry in enumerate(model.tensor_entries):
            if not entry.id:
                r.error(f"tensor_entries[{i}].id", "TensorEntry id must not be empty")
                continue
            if entry.id in seen:
                r.error(f"tensor_entries[{i}].id",
                        f"Duplicate constant name: {entry.id!r}")
            seen.add(entry.id)

    # ── functions ─────────────────────────────────────────────────────────────

    def _check_functions(self, model: OMLEModel, r: ValidationResult) -> None:
        seen: set[str] = set()
        for i, fn in enumerate(model.functions):
            if not fn.name:
                r.error(f"functions[{i}].name", "Function name must not be empty")
                continue
            if fn.name in seen:
                r.error(f"functions[{i}].name",
                        f"Duplicate function name: {fn.name!r}")
            seen.add(fn.name)

            # Check parameter name uniqueness
            param_names: set[str] = set()
            for j, param in enumerate(fn.parameters):
                if not param.name:
                    r.error(f"functions[{i}].parameters[{j}].name",
                            "Parameter name must not be empty")
                elif param.name in param_names:
                    r.error(f"functions[{i}].parameters[{j}].name",
                            f"Duplicate parameter name {param.name!r} in function {fn.name!r}")
                param_names.add(param.name)

        # Check for recursion (self-calls and mutual recursion)
        self._check_function_recursion(model.functions, r)

    def _check_function_recursion(self, functions: list[DefineFunction],
                                   r: ValidationResult) -> None:

        fn_names = {fn.name for fn in functions}

        def collect_calls(expr: Optional["Expression"]) -> set[str]:
            if expr is None:
                return set()
            calls: set[str] = set()
            if expr.apply:
                calls.add(expr.apply.function)
                for arg in expr.apply.arguments:
                    calls |= collect_calls(arg)
            return calls & fn_names

        # Build call graph
        call_graph: dict[str, set[str]] = {}
        for fn in functions:
            call_graph[fn.name] = collect_calls(fn.body)

        # DFS cycle check
        def has_cycle(name: str, visiting: set[str], visited: set[str]) -> bool:
            if name in visiting:
                return True
            if name in visited:
                return False
            visiting.add(name)
            for callee in call_graph.get(name, set()):
                if has_cycle(callee, visiting, visited):
                    return True
            visiting.discard(name)
            visited.add(name)
            return False

        visited: set[str] = set()
        for fn in functions:
            if has_cycle(fn.name, set(), visited):
                r.error(f"functions[{fn.name}]",
                        f"Function {fn.name!r} is involved in a recursive call cycle")


    # ── verification / warmup / sample_inputs ────────────────────────────────

    def _tensor_entry_ids(self, model: OMLEModel) -> set[str]:
        return {e.id for e in model.tensor_entries if e.id}

    def _check_tensor_refs(self, refs, path: str, valid_ids: set[str],
                           valid_names: Optional[set[str]], label: str,
                           r: ValidationResult) -> None:
        """Validate a list of TensorRefs: ids must exist; inner tensor names must
        match *valid_names* when provided."""
        seen_names: set[str] = set()
        for k, ref in enumerate(refs):
            ref_path = f"{path}[{k}]"
            if not ref.id:
                r.error(ref_path, f"{label} TensorRef id must not be empty")
                continue
            if ref.id not in valid_ids:
                r.error(ref_path,
                        f"{label} TensorRef {ref.id!r} does not match any tensor_entry id")
                continue
            if valid_names is not None:
                # Resolve to the inner tensor name
                entry = next((e for e in self._model_entries if e.id == ref.id), None)
                if entry is not None:
                    tensor = entry.dense if entry.dense is not None else entry.sparse
                    inner_name = tensor.name if tensor is not None else ""
                    if inner_name not in valid_names:
                        r.error(ref_path,
                                f"{label} tensor {ref.id!r} has inner name {inner_name!r} "
                                f"which does not match any model {label.lower()} name")
                    if inner_name in seen_names:
                        r.error(ref_path,
                                f"{label} tensor name {inner_name!r} appears more than once "
                                "in the same case")
                    seen_names.add(inner_name)

    def _check_verification(self, model: OMLEModel, r: ValidationResult) -> None:
        if not model.verification:
            return
        self._model_entries = model.tensor_entries
        valid_ids = self._tensor_entry_ids(model)
        input_names = {s.name for s in model.inputs}
        output_names = {s.name for s in model.outputs}

        v = model.verification
        if v.tolerance:
            tol = v.tolerance
            for field in ("atol", "rtol"):
                scalar = getattr(tol, field)
                if scalar is None:
                    continue
                # Tolerances round-trip through proto as Scalar messages, but
                # hand-built models often set a plain float; accept both.
                value = scalar.value if isinstance(scalar, Scalar) else scalar
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    r.error(f"verification.tolerance.{field}",
                            f"{field} must be a numeric scalar, got {value!r}")
                elif value < 0:
                    r.error(f"verification.tolerance.{field}",
                            f"{field} must be >= 0, got {value}")

        for i, case in enumerate(v.cases):
            base = f"verification.cases[{i}]"
            self._check_tensor_refs(case.inputs, f"{base}.inputs",
                                    valid_ids, input_names, "Input", r)
            self._check_tensor_refs(case.expected_outputs, f"{base}.expected_outputs",
                                    valid_ids, output_names, "Output", r)

    def _check_warmup(self, model: OMLEModel, r: ValidationResult) -> None:
        if not model.warmup:
            return
        self._model_entries = model.tensor_entries
        valid_ids = self._tensor_entry_ids(model)
        input_names = {s.name for s in model.inputs}

        for i, case in enumerate(model.warmup.cases):
            base = f"warmup.cases[{i}]"
            # repeat == 0 means "use default (1)"; negative values are invalid
            if case.repeat < 0:
                r.error(f"{base}.repeat",
                        f"repeat must be >= 0 (0 = default 1), got {case.repeat}")
            self._check_tensor_refs(case.inputs, f"{base}.inputs",
                                    valid_ids, input_names, "Input", r)

    def _check_sample_inputs(self, model: OMLEModel, r: ValidationResult) -> None:
        if not model.sample_inputs:
            return
        self._model_entries = model.tensor_entries
        valid_ids = self._tensor_entry_ids(model)
        input_names = {s.name for s in model.inputs}

        for i, case in enumerate(model.sample_inputs.cases):
            self._check_tensor_refs(case.inputs, f"sample_inputs.cases[{i}].inputs",
                                    valid_ids, input_names, "Input", r)

    # ── registry: operator imports ────────────────────────────────────────────

    def _check_operator_imports(self, model: OMLEModel, op_reg, r: ValidationResult) -> None:
        """Warn if a node uses a standard namespace not declared in operator_imports."""
        declared = {imp.namespace for imp in model.operator_imports}
        for i, node in enumerate(model.nodes):
            if not node.domain:
                continue
            if op_reg.known_namespace(node.domain) and node.domain not in declared:
                r.error(
                    f"nodes[{i}].domain",
                    f"Node {node.name!r} uses namespace {node.domain!r} "
                    "which is not declared in operator_imports",
                )

    # ── registry: per-node operator checks ───────────────────────────────────

    # Maps structured operator body_type → the attribute name on Node that should be set
    _BODY_TYPE_TO_FIELD: dict[str, str] = {
        "tree": "tree",
        "tree_ensemble": "tree_ensemble",
        "linear": "linear",
        "naive_bayes": "naive_bayes",
        "clustering": "clustering",
    }

    def _check_node_registry(self, node: Node, node_idx: int,
                              op_reg, r: ValidationResult,
                              tensor_entry_map: dict | None = None) -> None:
        if not node.domain or not node.op:
            return
        if not op_reg.known_namespace(node.domain):
            return  # vendor/custom namespace — skip

        op_def = op_reg.get(node.domain, node.op)
        if op_def is None:
            r.error(
                f"nodes[{node_idx}].op",
                f"Unknown operator {node.op!r} in namespace {node.domain!r}",
            )
            return

        path = f"nodes[{node_idx}]({node.name!r})"
        attr_map = {a.name: a for a in node.attributes}

        # Required attributes present
        for req in op_def.required_attrs():
            if req not in attr_map:
                r.error(path, f"Missing required attribute {req!r} for operator {node.op!r}")

        # Enum-constrained attribute values
        for attr_def in op_def.attributes:
            if not attr_def.enum_values:
                continue
            if attr_def.name not in attr_map:
                continue
            node_attr = attr_map[attr_def.name]
            val = node_attr.s  # enum attributes are always string-typed
            if val is not None and val not in attr_def.enum_values:
                r.error(
                    f"{path}.attributes[{attr_def.name!r}]",
                    f"Attribute {attr_def.name!r} value {val!r} is not a valid "
                    f"enum value; expected one of {attr_def.enum_values}",
                )

        # Structured operators: correct body field must be set
        if op_def.kind == "structured" and op_def.body_type:
            expected_field = self._BODY_TYPE_TO_FIELD.get(op_def.body_type)
            if expected_field and getattr(node, expected_field, None) is None:
                r.error(
                    path,
                    f"Operator {node.op!r} (kind=structured, body_type={op_def.body_type!r}) "
                    f"requires node.{expected_field} to be set",
                )

        # Operator-specific rules
        self._check_node_op_specific(node, node_idx, op_def, attr_map, r,
                                     tensor_entry_map or {})

    def _check_node_op_specific(self, node: Node, node_idx: int,
                                 op_def, attr_map: dict, r: ValidationResult,
                                 tensor_entry_map: dict | None = None) -> None:
        if tensor_entry_map is None:
            tensor_entry_map = {}
        path = f"nodes[{node_idx}]({node.name!r})"

        if op_def.name == "Split":
            sections_attr = attr_map.get("sections")
            if sections_attr is not None and sections_attr.ints is not None:
                sections = sections_attr.ints
                # Each section must be positive
                for k, s in enumerate(sections):
                    if s <= 0:
                        r.error(path, f"Split: sections[{k}] = {s} must be positive")
                # Number of outputs must equal len(sections)
                n_out = len(node.outputs)
                if n_out != len(sections):
                    r.error(
                        path,
                        f"Split: number of outputs ({n_out}) must equal "
                        f"len(sections) ({len(sections)})",
                    )

        elif op_def.name == "Imputer":
            has_fill_value = "fill_value" in attr_map
            has_fill_tensor = "fill_tensor" in attr_map
            if has_fill_value and has_fill_tensor:
                r.error(path, "Imputer: only one of fill_value or fill_tensor may be set")
            elif not has_fill_value and not has_fill_tensor:
                r.error(path, "Imputer: exactly one of fill_value or fill_tensor must be provided")

        elif op_def.name == "OneHotEncoder":
            categories_attr = attr_map.get("categories")
            k = None
            if categories_attr is not None:
                if categories_attr.strings is not None:
                    k = len(categories_attr.strings)
                elif (categories_attr.tensor_ref is not None
                      and categories_attr.tensor_ref.id in tensor_entry_map):
                    entry = tensor_entry_map[categories_attr.tensor_ref.id]
                    if entry.dense is not None and entry.dense.string_data is not None:
                        k = len(entry.dense.string_data)
            if k is not None:
                # Check declared output shape if present
                for out in node.outputs:
                    if out.type and len(out.type.shape) >= 2:
                        last_dim = out.type.shape[-1]
                        if last_dim != k:
                            r.error(
                                path,
                                f"OneHotEncoder: output last dimension ({last_dim}) "
                                f"must equal len(categories) ({k})",
                            )

    # ── registry: expression / function checks ────────────────────────────────

    def _check_expressions_registry(self, model: OMLEModel, fn_reg,
                                     imported_fn_ns: list[str],
                                     r: ValidationResult) -> None:
        """Walk all expressions in the model and validate function references."""

        # Expressions appear in:
        #   1. Node attributes of type "expression"
        #   2. DefineFunction bodies
        for i, node in enumerate(model.nodes):
            for attr in node.attributes:
                if attr.expr is not None:
                    self._check_expression(
                        attr.expr, f"nodes[{i}]({node.name!r}).attrs[{attr.name!r}]",
                        fn_reg, imported_fn_ns, r,
                    )

        for i, fn in enumerate(model.functions):
            if fn.body is not None:
                self._check_expression(
                    fn.body, f"functions[{i}]({fn.name!r}).body",
                    fn_reg, imported_fn_ns, r,
                )

    def _check_expression(self, expr: Expression, path: str,
                           fn_reg, imported_fn_ns: list[str],
                           r: ValidationResult) -> None:
        if expr.apply is None:
            return
        self._check_apply(expr.apply, path, fn_reg, imported_fn_ns, r)

    def _check_apply(self, apply: Apply, path: str,
                     fn_reg, imported_fn_ns: list[str],
                     r: ValidationResult) -> None:
        fn_name = apply.function

        # Only validate against the registry when there are function imports
        # OR when the name is unambiguously from a known namespace.
        fn_def = fn_reg.resolve(fn_name, imported_fn_ns)

        if imported_fn_ns and fn_def is None:
            # There are declared function namespaces but the name didn't resolve.
            r.error(
                path,
                f"Function {fn_name!r} does not resolve in imported function "
                f"namespaces {imported_fn_ns}",
            )
        elif fn_def is not None:
            # Validate argument count
            n_args = len(apply.arguments)
            min_a = fn_def.min_args
            max_a = fn_def.max_args  # None = unbounded

            if n_args < min_a:
                r.error(
                    path,
                    f"Function {fn_name!r} requires at least {min_a} argument(s), "
                    f"got {n_args}",
                )
            elif max_a is not None and n_args > max_a:
                r.error(
                    path,
                    f"Function {fn_name!r} accepts at most {max_a} argument(s), "
                    f"got {n_args}",
                )

            # map_values: pairs must be even
            if fn_def.name == "map_values" and n_args >= 1:
                # args[0] is x; the rest are pairs
                pair_count = n_args - 1
                if pair_count % 2 != 0:
                    r.error(
                        path,
                        f"map_values: pairs argument count must be even, "
                        f"got {pair_count} pair element(s)",
                    )

        # Recurse into arguments
        for k, arg in enumerate(apply.arguments):
            self._check_expression(arg, f"{path}.args[{k}]", fn_reg, imported_fn_ns, r)


def validate(model: OMLEModel, *, use_registry: bool = True) -> ValidationResult:
    """Validate an OMLEModel and return a ValidationResult."""
    return ModelValidator().validate(model, use_registry=use_registry)


def assert_valid(model: OMLEModel, *, use_registry: bool = True) -> None:
    """Validate a model and raise ValueError if invalid."""
    result = validate(model, use_registry=use_registry)
    if not result.is_valid:
        raise ValueError(str(result))
