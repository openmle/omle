"""Developer tool: validate OMLE operator and function registry files.

Validates two levels:
  1. The merged registry files (operators.json / functions.json) against
     their JSON schemas and structural rules.
  2. Each per-namespace source file against the namespace JSON schema and
     structural rules.

Usage::

    python tools/validate_registry.py
    python tools/validate_registry.py --operators-file path/to/operators.json
    python tools/validate_registry.py --functions-file path/to/functions.json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

# Allow running directly from the repo root without installing the package.
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

_RESET = "\033[0m"
_GREEN = "\033[32m"
_RED   = "\033[31m"
_DIM   = "\033[2m"


def _c(text: str, code: str) -> str:
    return f"{code}{text}{_RESET}" if sys.stdout.isatty() else text


def _green(t: str) -> str: return _c(t, _GREEN)
def _red(t: str)   -> str: return _c(t, _RED)
def _dim(t: str)   -> str: return _c(t, _DIM)


# ── Validation result ─────────────────────────────────────────────────────────

@dataclass
class RegistryError:
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


@dataclass
class RegistryValidationResult:
    file: str
    errors: List[RegistryError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add(self, path: str, message: str) -> None:
        self.errors.append(RegistryError(path=path, message=message))


# ── Operator structural validation ────────────────────────────────────────────

def _validate_operator_attribute(attr: object, path: str,
                                  result: RegistryValidationResult) -> None:
    if not isinstance(attr, dict):
        result.add(path, "attribute must be an object")
        return
    if not attr.get("name"):
        result.add(path, "attribute missing 'name'")
    t = attr.get("type")
    valid_types = {
        "string", "int", "float", "bool",
        "ints", "floats", "strings", "bools",
        "tensor_ref", "tensor_like", "expression", "predicate", "scalar",
    }
    if t and t not in valid_types:
        result.add(path, f"unknown attribute type {t!r}; expected one of {sorted(valid_types)}")
    enum_vals = attr.get("enum_values")
    if enum_vals is not None and (not isinstance(enum_vals, list) or len(enum_vals) == 0):
        result.add(path, "'enum_values' must be a non-empty list when present")


def _validate_operator(op: object, ns_name: str, idx: int,
                        result: RegistryValidationResult) -> None:
    path = f"namespaces[{ns_name!r}].operators[{idx}]"
    if not isinstance(op, dict):
        result.add(path, "operator entry must be an object")
        return

    for req in ("name", "summary", "kind"):
        if not op.get(req):
            result.add(path, f"missing required field {req!r}")

    kind = op.get("kind")
    if kind not in (None, "generic", "structured"):
        result.add(path, f"invalid kind {kind!r}; must be 'generic' or 'structured'")

    body_type = op.get("body_type")
    if kind == "structured" and not body_type:
        result.add(path, "structured operator must have 'body_type'")
    if kind == "generic" and body_type:
        result.add(path, "generic operator should not have 'body_type'")

    input_names: List[str] = []
    for i, inp in enumerate(op.get("inputs", [])):
        ipath = f"{path}.inputs[{i}]"
        if not isinstance(inp, dict):
            result.add(ipath, "input must be an object")
            continue
        if not inp.get("name"):
            result.add(ipath, "input missing 'name'")
        else:
            name = inp["name"]
            if name in input_names:
                result.add(ipath, f"duplicate input name {name!r}")
            input_names.append(name)

    attr_names: List[str] = []
    for i, attr in enumerate(op.get("attributes", [])):
        apath = f"{path}.attributes[{i}]"
        _validate_operator_attribute(attr, apath, result)
        name = attr.get("name") if isinstance(attr, dict) else None
        if name:
            if name in attr_names:
                result.add(apath, f"duplicate attribute name {name!r}")
            attr_names.append(name)


def _validate_operator_namespace_body(ns: dict, ns_name: str,
                                       result: RegistryValidationResult) -> None:
    operators = ns.get("operators", [])
    if not isinstance(operators, list):
        result.add(f"namespaces[{ns_name!r}].operators", "must be a list")
        return
    op_names: List[str] = []
    for i, op in enumerate(operators):
        _validate_operator(op, ns_name, i, result)
        op_name = op.get("name") if isinstance(op, dict) else None
        if op_name:
            if op_name in op_names:
                result.add(f"namespaces[{ns_name!r}].operators[{i}]",
                           f"duplicate operator name {op_name!r}")
            op_names.append(op_name)


def validate_operator_namespace(data: object, file: str) -> RegistryValidationResult:
    """Validate a single per-namespace operator file."""
    result = RegistryValidationResult(file=file)
    if not isinstance(data, dict):
        result.add("$", "namespace file must be a JSON object")
        return result
    for req in ("name", "version", "description"):
        if not data.get(req):
            result.add(req, "missing or empty")
    ns_name = data.get("name", "<unknown>")
    _validate_operator_namespace_body(data, ns_name, result)
    return result


def validate_operator_registry(data: object, file: str = "operators.json"
                                ) -> RegistryValidationResult:
    """Validate the merged operators registry file."""
    result = RegistryValidationResult(file=file)
    if not isinstance(data, dict):
        result.add("$", "registry must be a JSON object")
        return result

    if data.get("registry_type") != "operators":
        result.add("registry_type", f"expected 'operators', got {data.get('registry_type')!r}")
    if not data.get("registry_version"):
        result.add("registry_version", "missing or empty")
    if not data.get("description"):
        result.add("description", "missing or empty")

    namespaces = data.get("namespaces", [])
    if not isinstance(namespaces, list):
        result.add("namespaces", "must be a list")
        return result

    ns_names: List[str] = []
    for ni, ns in enumerate(namespaces):
        npath = f"namespaces[{ni}]"
        if not isinstance(ns, dict):
            result.add(npath, "namespace entry must be an object")
            continue
        ns_name = ns.get("name", f"<{ni}>")
        if not ns.get("name"):
            result.add(npath, "namespace missing 'name'")
        else:
            if ns_name in ns_names:
                result.add(npath, f"duplicate namespace {ns_name!r}")
            ns_names.append(ns_name)
        _validate_operator_namespace_body(ns, ns_name, result)

    return result


# ── Function structural validation ────────────────────────────────────────────

def _validate_function(fn: object, ns_name: str, idx: int,
                        result: RegistryValidationResult) -> None:
    path = f"namespaces[{ns_name!r}].functions[{idx}]"
    if not isinstance(fn, dict):
        result.add(path, "function entry must be an object")
        return

    for req in ("name", "summary"):
        if not fn.get(req):
            result.add(path, f"missing required field {req!r}")

    arg_names: List[str] = []
    variadic_seen = False
    for i, arg in enumerate(fn.get("arguments", [])):
        apath = f"{path}.arguments[{i}]"
        if not isinstance(arg, dict):
            result.add(apath, "argument must be an object")
            continue
        if not arg.get("name"):
            result.add(apath, "argument missing 'name'")
        else:
            name = arg["name"]
            if name in arg_names:
                result.add(apath, f"duplicate argument name {name!r}")
            arg_names.append(name)
        is_variadic = arg.get("variadic", False)
        if variadic_seen and not is_variadic:
            result.add(apath, "only the last argument may be variadic")
        if is_variadic:
            variadic_seen = True

    opt_names: List[str] = []
    for i, p in enumerate(fn.get("optional_parameters", [])):
        ppath = f"{path}.optional_parameters[{i}]"
        if not isinstance(p, dict):
            result.add(ppath, "optional_parameter must be an object")
            continue
        if not p.get("name"):
            result.add(ppath, "optional_parameter missing 'name'")
        else:
            name = p["name"]
            if name in opt_names:
                result.add(ppath, f"duplicate optional parameter {name!r}")
            opt_names.append(name)

    if not fn.get("returns"):
        result.add(path, "function missing 'returns'")


def _validate_function_namespace_body(ns: dict, ns_name: str,
                                       result: RegistryValidationResult) -> None:
    functions = ns.get("functions", [])
    if not isinstance(functions, list):
        result.add(f"namespaces[{ns_name!r}].functions", "must be a list")
        return
    fn_names: List[str] = []
    for i, fn in enumerate(functions):
        _validate_function(fn, ns_name, i, result)
        fn_name = fn.get("name") if isinstance(fn, dict) else None
        if fn_name:
            if fn_name in fn_names:
                result.add(f"namespaces[{ns_name!r}].functions[{i}]",
                           f"duplicate function name {fn_name!r}")
            fn_names.append(fn_name)


def validate_function_namespace(data: object, file: str) -> RegistryValidationResult:
    """Validate a single per-namespace function file."""
    result = RegistryValidationResult(file=file)
    if not isinstance(data, dict):
        result.add("$", "namespace file must be a JSON object")
        return result
    for req in ("name", "version", "description"):
        if not data.get(req):
            result.add(req, "missing or empty")
    ns_name = data.get("name", "<unknown>")
    _validate_function_namespace_body(data, ns_name, result)
    return result


def validate_function_registry(data: object, file: str = "functions.json"
                                ) -> RegistryValidationResult:
    """Validate the merged functions registry file."""
    result = RegistryValidationResult(file=file)
    if not isinstance(data, dict):
        result.add("$", "registry must be a JSON object")
        return result

    if data.get("registry_type") != "functions":
        result.add("registry_type", f"expected 'functions', got {data.get('registry_type')!r}")
    if not data.get("registry_version"):
        result.add("registry_version", "missing or empty")
    if not data.get("description"):
        result.add("description", "missing or empty")

    namespaces = data.get("namespaces", [])
    if not isinstance(namespaces, list):
        result.add("namespaces", "must be a list")
        return result

    ns_names: List[str] = []
    for ni, ns in enumerate(namespaces):
        npath = f"namespaces[{ni}]"
        if not isinstance(ns, dict):
            result.add(npath, "namespace entry must be an object")
            continue
        ns_name = ns.get("name", f"<{ni}>")
        if not ns.get("name"):
            result.add(npath, "namespace missing 'name'")
        else:
            if ns_name in ns_names:
                result.add(npath, f"duplicate namespace {ns_name!r}")
            ns_names.append(ns_name)
        _validate_function_namespace_body(ns, ns_name, result)

    return result


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_json(path: Path) -> Tuple[Optional[dict], Optional[str]]:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, f"file not found: {path}"
    except json.JSONDecodeError as e:
        return None, f"invalid JSON: {e}"


def _jsonschema_available() -> bool:
    try:
        import jsonschema  # type: ignore  # noqa: F401
        return True
    except ImportError:
        return False


def _apply_schema_validation(data: dict, schema_path: Path,
                              result: RegistryValidationResult) -> None:
    import jsonschema  # type: ignore

    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)

    # Load all sibling schemas into a registry so cross-file $refs
    # (e.g. "operators.schema.json#/$defs/operator") can be resolved.
    import referencing  # type: ignore
    import referencing.jsonschema as ref_js  # type: ignore

    resources = []
    for sibling in schema_path.parent.glob("*.json"):
        with open(sibling, encoding="utf-8") as f:
            s = json.load(f)
        if "$id" in s:
            resources.append((s["$id"], ref_js.DRAFT202012.create_resource(s)))
    registry = referencing.Registry().with_resources(resources)

    validator = jsonschema.Draft202012Validator(schema, registry=registry)
    for err in validator.iter_errors(data):
        loc = ".".join(str(p) for p in err.absolute_path) or "$"
        result.add(loc, f"[schema] {err.message}")


# ── Main validation logic ─────────────────────────────────────────────────────

def validate_registry_files(
    operators_path: Optional[Path] = None,
    functions_path: Optional[Path] = None,
) -> List[RegistryValidationResult]:
    """Validate both registry kinds and return one result per file checked.

    For each kind:
      - Validates the merged .v1.json file (explicit path or source default)
        against structural rules and operators.schema.json / functions.schema.json.
      - Validates every per-namespace file under registries/<kind>/namespaces/
        against structural rules and operators.namespace.schema.json /
        functions.namespace.schema.json.
    """
    from omle.registry import _REGISTRIES_SRC

    schema_validation = _jsonschema_available()
    if not schema_validation:
        print(
            "warning: jsonschema is not installed — JSON Schema validation skipped. "
            "Run: pip install jsonschema",
            file=sys.stderr,
        )

    results: List[RegistryValidationResult] = []

    specs = [
        (operators_path, "operators", validate_operator_registry,
         validate_operator_namespace, "operators.json",
         "operators.schema.json", "operators.namespace.schema.json"),
        (functions_path, "functions", validate_function_registry,
         validate_function_namespace, "functions.json",
         "functions.schema.json", "functions.namespace.schema.json"),
    ]

    for (explicit_path, kind, merged_validator, ns_validator,
         merged_label, merged_schema_name, ns_schema_name) in specs:

        kind_dir = _REGISTRIES_SRC / kind
        schema_dir = kind_dir / "schema"
        merged_schema = schema_dir / merged_schema_name
        ns_schema = schema_dir / ns_schema_name

        # ── Merged file ────────────────────────────────────────────────────
        if explicit_path is not None:
            merged_file = explicit_path
        else:
            merged_file = kind_dir / merged_label

        data, err = _load_json(merged_file)
        r = RegistryValidationResult(file=str(merged_file))
        if err:
            r.add("$", err)
        else:
            r = merged_validator(data, file=str(merged_file))
            if schema_validation and merged_schema.exists():
                _apply_schema_validation(data, merged_schema, r)
        results.append(r)

        # ── Per-namespace files ────────────────────────────────────────────
        ns_dir = kind_dir / "namespaces"
        if ns_dir.is_dir():
            for ns_file in sorted(ns_dir.glob("*.json")):
                ns_data, ns_err = _load_json(ns_file)
                nr = RegistryValidationResult(file=str(ns_file))
                if ns_err:
                    nr.add("$", ns_err)
                else:
                    nr = ns_validator(ns_data, file=str(ns_file))
                    if schema_validation and ns_schema.exists():
                        _apply_schema_validation(ns_data, ns_schema, nr)
                results.append(nr)

    return results


# ── Entry point ───────────────────────────────────────────────────────────────

def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        prog="validate_registry",
        description=(
            "Structurally validate operators.json / functions.json and "
            "their per-namespace source files for missing required fields, "
            "duplicates, and schema conformance."
        ),
    )
    parser.add_argument(
        "--operators-file",
        metavar="FILE",
        default=None,
        help="Path to merged operators registry JSON (default: registries/operators/operators.json)",
    )
    parser.add_argument(
        "--functions-file",
        metavar="FILE",
        default=None,
        help="Path to merged functions registry JSON (default: registries/functions/functions.json)",
    )
    args = parser.parse_args(argv)

    op_path = Path(args.operators_file) if args.operators_file else None
    fn_path = Path(args.functions_file) if args.functions_file else None

    results = validate_registry_files(op_path, fn_path)
    all_valid = True
    for r in results:
        label = Path(r.file).name
        if r.is_valid:
            print(_green("✓") + f" {label} is valid")
        else:
            all_valid = False
            n = len(r.errors)
            print(_red("✗") + f" {label}: {n} error{'s' if n != 1 else ''}")
            for err in r.errors:
                print(f"  {_dim(err.path)}")
                print(f"    {err.message}")
    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()
