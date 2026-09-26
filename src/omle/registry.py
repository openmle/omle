"""OMLE registry loader.

Parses operators.json and functions.json and exposes structured lookup
objects used by the validator.

Resolution order:
  1. Bundled registry — omle/registry/ inside the installed wheel (written by
     the build hook in setup.py, which merges per-namespace source files).
  2. Source registry  — registries/ in the repo root, merged on-the-fly.
     Used when running directly from a checkout without building/installing.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Bundled path: populated at build time by setup.py.
_BUNDLED_REGISTRY = Path(__file__).parent / "registry"

# Source path: per-namespace files live under registries/ in the repo root.
# Path(__file__) = src/omle/registry.py  →  parent×3 = repo root
_REGISTRIES_SRC = Path(__file__).parent.parent.parent / "registries"

# Kept for backward-compat imports in registry_tools.py and tests.
_REGISTRY_DIR = _BUNDLED_REGISTRY


def _merge_registry_data(kind: str) -> dict:
    """Merge per-namespace source files into one registry dict.

    Reads ``registries/<kind>/<kind>.json`` (base template containing global
    metadata and empty ``namespaces``) and all
    ``registries/<kind>/namespaces/*.json`` files, injects them as the
    ``namespaces`` list, and returns the complete dict.
    """
    kind_dir = _REGISTRIES_SRC / kind
    base_path = kind_dir / f"{kind}.json"
    ns_dir = kind_dir / "namespaces"
    with open(base_path, encoding="utf-8") as f:
        data = json.load(f)
    namespaces = []
    if ns_dir.is_dir():
        for ns_file in sorted(ns_dir.glob("*.json")):
            with open(ns_file, encoding="utf-8") as f:
                namespaces.append(json.load(f))
    data["namespaces"] = namespaces
    return data


# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class AttributeDef:
    name: str
    type: str
    required: bool
    default: object = None
    enum_values: list[str] = field(default_factory=list)


@dataclass
class OperatorDef:
    name: str
    namespace: str
    kind: str                          # "generic" or "structured"
    body_type: Optional[str]           # e.g. "linear", "tree_ensemble" for structured
    attributes: list[AttributeDef]
    validation_rules: list[str]
    min_inputs: int                    # number of required (non-variadic) inputs
    has_variadic_input: bool

    def required_attrs(self) -> list[str]:
        return [a.name for a in self.attributes if a.required]

    def optional_attrs(self) -> list[str]:
        return [a.name for a in self.attributes if not a.required]

    def attr_def(self, name: str) -> Optional[AttributeDef]:
        for a in self.attributes:
            if a.name == name:
                return a
        return None


@dataclass
class ArgumentDef:
    name: str
    kinds: list[str]
    variadic: bool = False


@dataclass
class FunctionDef:
    name: str
    namespace: str
    positional_args: list[ArgumentDef]   # includes the variadic one if any
    optional_params: list[str]           # optional named parameters

    @property
    def min_args(self) -> int:
        """Minimum number of positional arguments required."""
        return sum(1 for a in self.positional_args if not a.variadic)

    @property
    def is_variadic(self) -> bool:
        return any(a.variadic for a in self.positional_args)

    @property
    def max_args(self) -> Optional[int]:
        """Maximum positional argument count, or None if unbounded (variadic)."""
        if self.is_variadic:
            return None
        return len(self.positional_args)


# ── Registry containers ───────────────────────────────────────────────────────

class OperatorRegistry:
    """Lookup table for operator definitions keyed by (namespace, op_name)."""

    def __init__(self, operators: dict[tuple[str, str], OperatorDef]) -> None:
        self._ops = operators
        self._namespaces: set[str] = {ns for ns, _ in operators}

    def get(self, namespace: str, op_name: str) -> Optional[OperatorDef]:
        return self._ops.get((namespace, op_name))

    def known_namespace(self, namespace: str) -> bool:
        return namespace in self._namespaces

    @property
    def namespaces(self) -> set[str]:
        return set(self._namespaces)


class FunctionRegistry:
    """Lookup table for function definitions keyed by (namespace, fn_name)."""

    def __init__(self, functions: dict[tuple[str, str], FunctionDef]) -> None:
        self._fns = functions
        self._namespaces: set[str] = {ns for ns, _ in functions}

    def get(self, namespace: str, fn_name: str) -> Optional[FunctionDef]:
        return self._fns.get((namespace, fn_name))

    def known_namespace(self, namespace: str) -> bool:
        return namespace in self._namespaces

    def resolve(self, fn_name: str,
                imported_namespaces: list[str]) -> Optional[FunctionDef]:
        """Resolve an unqualified or qualified function name against imported namespaces."""
        # Qualified: "omle.functions.log" or "omle.functions/log"
        for sep in (".", "/"):
            if sep in fn_name:
                parts = fn_name.rsplit(sep, 1)
                return self._fns.get((parts[0], parts[1]))
        # Unqualified: search imported namespaces in order
        for ns in imported_namespaces:
            fn = self._fns.get((ns, fn_name))
            if fn is not None:
                return fn
        return None

    @property
    def namespaces(self) -> set[str]:
        return set(self._namespaces)


# ── Parsers ───────────────────────────────────────────────────────────────────

def _parse_operator_registry(data: dict) -> OperatorRegistry:
    ops: dict[tuple[str, str], OperatorDef] = {}
    for ns_entry in data.get("namespaces", []):
        ns = ns_entry["name"]
        for op_raw in ns_entry.get("operators", []):
            attrs: list[AttributeDef] = []
            for a in op_raw.get("attributes", []):
                attrs.append(AttributeDef(
                    name=a["name"],
                    type=a.get("type", "string"),
                    required=a.get("required", False),
                    default=a.get("default"),
                    enum_values=a.get("enum_values", []),
                ))

            inputs = op_raw.get("inputs", [])
            required_inputs = sum(1 for i in inputs if i.get("required", True)
                                  and not i.get("variadic", False))
            has_variadic = any(i.get("variadic", False) for i in inputs)

            ops[(ns, op_raw["name"])] = OperatorDef(
                name=op_raw["name"],
                namespace=ns,
                kind=op_raw.get("kind", "generic"),
                body_type=op_raw.get("body_type"),
                attributes=attrs,
                validation_rules=op_raw.get("validation_rules", []),
                min_inputs=required_inputs,
                has_variadic_input=has_variadic,
            )
    return OperatorRegistry(ops)


def _parse_function_registry(data: dict) -> FunctionRegistry:
    fns: dict[tuple[str, str], FunctionDef] = {}
    for ns_entry in data.get("namespaces", []):
        ns = ns_entry["name"]
        for fn_raw in ns_entry.get("functions", []):
            pos_args: list[ArgumentDef] = []
            for a in fn_raw.get("arguments", []):
                pos_args.append(ArgumentDef(
                    name=a["name"],
                    kinds=a.get("kinds", ["any"]),
                    variadic=a.get("variadic", False),
                ))
            optional_params = [p["name"] for p in fn_raw.get("optional_parameters", [])]
            fns[(ns, fn_raw["name"])] = FunctionDef(
                name=fn_raw["name"],
                namespace=ns,
                positional_args=pos_args,
                optional_params=optional_params,
            )
    return FunctionRegistry(fns)


# ── Public loaders ────────────────────────────────────────────────────────────

def load_operator_registry(path: Optional[Path] = None) -> OperatorRegistry:
    """Load the operator registry.

    If *path* is given, read that merged JSON file directly.
    Otherwise try the bundled registry first; fall back to merging from source.
    """
    if path is not None:
        with open(path, encoding="utf-8") as f:
            return _parse_operator_registry(json.load(f))
    bundled = _BUNDLED_REGISTRY / "operators.json"
    if bundled.exists():
        with open(bundled, encoding="utf-8") as f:
            return _parse_operator_registry(json.load(f))
    return _parse_operator_registry(_merge_registry_data("operators"))


def load_function_registry(path: Optional[Path] = None) -> FunctionRegistry:
    """Load the function registry.

    If *path* is given, read that merged JSON file directly.
    Otherwise try the bundled registry first; fall back to merging from source.
    """
    if path is not None:
        with open(path, encoding="utf-8") as f:
            return _parse_function_registry(json.load(f))
    bundled = _BUNDLED_REGISTRY / "functions.json"
    if bundled.exists():
        with open(bundled, encoding="utf-8") as f:
            return _parse_function_registry(json.load(f))
    return _parse_function_registry(_merge_registry_data("functions"))


def _raw_registry_data(kind: str) -> dict:
    """The registry JSON as stored, bundled copy first, merged source second.

    Same resolution order as the loaders above, but without parsing into
    OperatorDef/FunctionDef — namespace versions live on the namespace entries,
    which those structures drop.
    """
    bundled = _BUNDLED_REGISTRY / f"{kind}.json"
    if bundled.exists():
        with open(bundled, encoding="utf-8") as f:
            return json.load(f)
    return _merge_registry_data(kind)


def namespace_versions() -> dict[str, str]:
    """Map every registry namespace to its declared version, e.g. omle.core → 0.1.

    This is the source of truth for the version a producer records in a model's
    ``operator_imports``. Operator sets are versioned per namespace and move
    independently of both the schema version (``omle.FORMAT_VERSION``) and this
    package's release version, so a converter that hardcodes the numbers drifts
    the first time a namespace is bumped.
    """
    global _namespace_versions
    if _namespace_versions is None:
        out: dict[str, str] = {}
        for kind in ("operators", "functions"):
            for ns in _raw_registry_data(kind).get("namespaces", []):
                name, ver = ns.get("name"), ns.get("version")
                if name and ver:
                    out[name] = str(ver)
        _namespace_versions = out
    return dict(_namespace_versions)


# ── Cached singletons ─────────────────────────────────────────────────────────

_operator_registry: Optional[OperatorRegistry] = None
_function_registry: Optional[FunctionRegistry] = None
_namespace_versions: Optional[dict[str, str]] = None


def get_operator_registry() -> OperatorRegistry:
    """Return the cached singleton operator registry."""
    global _operator_registry
    if _operator_registry is None:
        _operator_registry = load_operator_registry()
    return _operator_registry


def get_function_registry() -> FunctionRegistry:
    """Return the cached singleton function registry."""
    global _function_registry
    if _function_registry is None:
        _function_registry = load_function_registry()
    return _function_registry
