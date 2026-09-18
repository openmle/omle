"""OMLE command-line interface.

Usage::

    omle validate model.omle
    omle validate model.omle --no-registry
    omle inspect  model.omle
    omle inspect  model.omle --section nodes
    omle inspect  model.omle --section metadata
    omle inspect  model.omle --section verification
    omle inspect  model.omle --section warmup
    omle inspect  model.omle --section sample_inputs
    omle inspect  model.omle --json

    omle convert xgboost  model.json    output.omle
    omle convert lightgbm model.txt     output.omle
    omle convert sklearn  model.joblib  output.omle
    omle convert pmml     model.pmml    output.omle
    omle convert treelite model.tl      output.omle

    omle view model.omle
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

# ── Formatting helpers ────────────────────────────────────────────────────────

_RESET  = "\033[0m"
_BOLD   = "\033[1m"
_GREEN  = "\033[32m"
_RED    = "\033[31m"
_YELLOW = "\033[33m"
_CYAN   = "\033[36m"
_DIM    = "\033[2m"


def _supports_color() -> bool:
    import os
    return sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def _c(text: str, code: str) -> str:
    return f"{code}{text}{_RESET}" if _supports_color() else text


def _bold(t: str)   -> str: return _c(t, _BOLD)
def _green(t: str)  -> str: return _c(t, _GREEN)
def _red(t: str)    -> str: return _c(t, _RED)
def _yellow(t: str) -> str: return _c(t, _YELLOW)
def _cyan(t: str)   -> str: return _c(t, _CYAN)
def _dim(t: str)    -> str: return _c(t, _DIM)


def _fmt_shape(shape: list[int]) -> str:
    if not shape:
        return "scalar"
    dims = ["N" if i == 0 else str(d) for i, d in enumerate(shape)]
    return "[" + ", ".join(dims) + "]"


def _fmt_type(type_obj) -> str:
    if type_obj is None:
        return ""
    dtype = type_obj.dtype.name if type_obj.dtype else ""
    shape = _fmt_shape(type_obj.shape)
    return f"{dtype}{shape}"


def _fmt_scalar(s) -> str:
    if s is None:
        return "null"
    v = s.value
    if isinstance(v, str):
        return repr(v)
    return str(v)


def _section_header(title: str) -> str:
    return _bold(title)


def _indent(text: str, n: int = 2) -> str:
    pad = " " * n
    return "\n".join(pad + line for line in text.splitlines())


# ── Load helper ───────────────────────────────────────────────────────────────

def _load_model(path: Path):
    """Load a model from path, printing a friendly error on failure."""
    from .io import load
    try:
        return load(path)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except FileNotFoundError:
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error loading {path}: {e}", file=sys.stderr)
        sys.exit(2)


# ── validate subcommand ───────────────────────────────────────────────────────

def _cmd_validate(args: argparse.Namespace) -> int:
    from .validation import validate

    path = Path(args.file)
    model = _load_model(path)
    result = validate(model, use_registry=not args.no_registry)

    if result.is_valid:
        print(_green("✓") + f" {path.name} is valid")
        return 0
    else:
        n = len(result.errors)
        print(_red("✗") + f" {path.name}: {n} error{'s' if n != 1 else ''}")
        for err in result.errors:
            print(f"  {_dim(err.path)}")
            print(f"    {err.message}")
        return 1


# ── inspect subcommand ────────────────────────────────────────────────────────

_ALL_SECTIONS = ("metadata", "imports", "inputs", "outputs", "schema",
                 "nodes", "tensor_entries", "functions",
                 "verification", "warmup", "sample_inputs")


def _inspect_metadata(model) -> list[str]:
    m = model.metadata
    lines = [_section_header("Metadata")]
    fields = [
        ("name",             m.name),
        ("format_version",   m.format_version),
        ("producer",         m.producer),
        ("producer_version", m.producer_version),
        ("doc_string",       m.doc_string),
    ]
    for label, value in fields:
        if value:
            lines.append(f"  {_dim(label + ':'): <30} {value}")
    for sf in m.source_frameworks:
        parts = sf.name
        if sf.version:
            parts += f" {sf.version}"
        if sf.role:
            parts += f" ({sf.role})"
        lines.append(f"  {_dim('source_framework:'): <30} {parts}")
    if m.attributes:
        for k, v in m.attributes.items():
            lines.append(f"  {_dim('attr:' + k + ':'): <30} {v}")
    return lines


def _inspect_imports(model) -> list[str]:
    lines = []
    if model.operator_imports:
        lines.append(_section_header(f"Operator Imports ({len(model.operator_imports)})"))
        for imp in model.operator_imports:
            lines.append(f"  {imp.namespace}  {_dim('v' + imp.version)}")
    if model.function_imports:
        lines.append(_section_header(f"Function Imports ({len(model.function_imports)})"))
        for imp in model.function_imports:
            lines.append(f"  {imp.namespace}  {_dim('v' + imp.version)}")
    return lines


def _inspect_inputs(model) -> list[str]:
    lines = [_section_header(f"Inputs ({len(model.inputs)})")]
    for spec in model.inputs:
        t = _fmt_type(spec.type)
        desc = f"  {_dim('—')} {spec.description}" if spec.description else ""
        lines.append(f"  {_cyan(spec.name): <24} {t}{desc}")
    return lines


def _inspect_outputs(model) -> list[str]:
    lines = [_section_header(f"Outputs ({len(model.outputs)})")]
    for spec in model.outputs:
        t = _fmt_type(spec.type)
        role = spec.role.name if spec.role.value != 0 else ""
        parts = [f"  {_cyan(spec.name): <24}", t]
        if role:
            parts.append(_yellow(role))
        if spec.binding and spec.binding.target_name:
            parts.append(_dim(f"→ {spec.binding.target_name}"))
        if spec.description:
            parts.append(_dim(f"— {spec.description}"))
        lines.append("  ".join(p for p in parts if p.strip()))
    return lines


def _inspect_schema(model) -> list[str]:
    if not model.model_schema:
        return [_section_header("Schema") + "  " + _dim("(none)")]
    schema = model.model_schema
    lines = [_section_header("Schema")]

    if schema.features:
        lines.append(f"  {_bold('Features')} ({len(schema.features)})")
        for feat in schema.features:
            names = feat.expand_names()
            name_str = ", ".join(names[:5])
            if len(names) > 5:
                name_str += f"  … (+{len(names) - 5} more)"
            t = _fmt_type(feat.type)
            ml = feat.measure_level.name if feat.measure_level.value != 0 else ""
            src = f"← {feat.source}[{feat.index}]" if feat.source else ""
            parts = [name_str, t, _yellow(ml) if ml else "", _dim(src) if src else ""]
            lines.append("    " + "  ".join(p for p in parts if p))

    if schema.targets:
        lines.append(f"  {_bold('Targets')} ({len(schema.targets)})")
        for tgt in schema.targets:
            t = _fmt_type(tgt.type)
            kind = tgt.kind.name if tgt.kind.value != 0 else ""
            labels = ""
            if tgt.class_labels:
                sample = [_fmt_scalar(s) for s in tgt.class_labels[:4]]
                if len(tgt.class_labels) > 4:
                    sample.append(f"… +{len(tgt.class_labels) - 4}")
                labels = "{" + ", ".join(sample) + "}"
            parts = [_cyan(tgt.name), t, _yellow(kind) if kind else "", labels]
            lines.append("    " + "  ".join(p for p in parts if p))

    return lines


def _inspect_nodes(model, verbose: bool = False) -> list[str]:
    lines = [_section_header(f"Nodes ({len(model.nodes)})")]
    for i, node in enumerate(model.nodes):
        domain_op = f"{node.domain}/{node.op}" if node.domain else node.op
        lines.append(f"  [{i}] {_cyan(node.name): <24} {_bold(domain_op)}")

        # inputs
        input_names = []
        for inp in node.inputs:
            if inp.name:
                ref = inp.name
                label = f"{ref.value}.{ref.field}" if ref.field else ref.value
                input_names.append(label)
            elif inp.range:
                r = inp.range
                input_names.append(f"{r.prefix}[{r.start}..{r.end})")
        if input_names:
            lines.append(f"      {'inputs': <10} {', '.join(input_names)}")

        # outputs
        for out in node.outputs:
            t = _fmt_type(out.type)
            role = out.role.name if out.role.value != 0 else ""
            parts = [out.name, t, _yellow(role) if role else ""]
            lines.append(f"      {'output': <10} " + "  ".join(p for p in parts if p))

        # body summary
        body = node.body()
        if body is not None:
            body_name = type(body).__name__
            details = _body_summary(body)
            lines.append(f"      {'body': <10} {_dim(body_name)}  {details}")

        # attributes (verbose)
        if verbose and node.attributes:
            for attr in node.attributes:
                val = _attr_value_str(attr)
                lines.append(f"      {'attr': <10} {attr.name} = {val}")

    return lines


def _body_summary(body) -> str:
    from .ir.bodies import (
        Clustering,
        Linear,
        NaiveBayes,
        Tree,
        TreeEnsemble,
    )
    if isinstance(body, Linear):
        pt = body.post_transform.name if body.post_transform.value != 0 else ""
        coef = (body.coefficients.tensor_ref.id if body.coefficients.tensor_ref else
                "inline" if body.coefficients.tensor or body.coefficients.sparse else "")
        return (f"coef={coef}"
                + ("  bias=inline" if body.intercept else "")
                + (f"  post={pt}" if pt else ""))
    if isinstance(body, TreeEnsemble):
        return (f"{len(body.trees)} trees"
                f"  agg={body.aggregation.name}"
                + (f"  base={body.base_score}" if body.base_score is not None else ""))
    if isinstance(body, Tree):
        return f"{body.num_nodes} nodes"
    if isinstance(body, NaiveBayes):
        variant = next(
            (name for name in ("gaussian", "multinomial", "bernoulli", "categorical")
             if getattr(body, name) is not None),
            "?",
        )
        priors = (body.class_log_priors.tensor_ref.id if body.class_log_priors.tensor_ref else
                  "inline" if body.class_log_priors.tensor or body.class_log_priors.sparse else "")
        return f"{variant}  priors={priors}"
    if isinstance(body, Clustering):
        if body.prototype:
            return f"prototype  dist={body.prototype.distance_measure.name}"
        if body.gaussian_mixture:
            return f"gaussian_mixture  cov={body.gaussian_mixture.covariance_type.name}"
    return ""


def _attr_value_str(attr) -> str:
    if attr.i is not None:
        return str(attr.i)
    if attr.f32 is not None:
        return str(attr.f32)
    if attr.f64 is not None:
        return str(attr.f64)
    if attr.s is not None:
        return repr(attr.s)
    if attr.b is not None:
        return str(attr.b)
    if attr.ints is not None:
        return f"[{', '.join(str(v) for v in attr.ints[:6])}{'…' if len(attr.ints) > 6 else ''}]"
    if attr.float32s is not None:
        return f"[{', '.join(f'{v:.4g}' for v in attr.float32s[:6])}{'…' if len(attr.float32s) > 6 else ''}]"
    if attr.float64s is not None:
        return f"[{', '.join(f'{v:.4g}' for v in attr.float64s[:6])}{'…' if len(attr.float64s) > 6 else ''}]"
    if attr.strings is not None:
        return f"[{', '.join(repr(v) for v in attr.strings[:4])}{'…' if len(attr.strings) > 4 else ''}]"
    if attr.tensor_ref is not None:
        return f"tensor_ref({attr.tensor_ref.id!r})"
    if attr.tensor is not None:
        return "<inline_tensor>"
    if attr.sparse is not None:
        return "<inline_sparse>"
    if attr.expr is not None:
        return "<expression>"
    if attr.predicate is not None:
        return "<predicate>"
    return ""


def _inspect_tensor_entries(model) -> list[str]:
    lines = [_section_header(f"Tensor entries ({len(model.tensor_entries)})")]
    for entry in model.tensor_entries:
        tensor = entry.dense if entry.dense is not None else entry.sparse
        if tensor is None:
            continue
        t = _fmt_type(tensor.type)
        counts = []
        if entry.dense is not None:
            for field in ("float32_data", "float64_data", "int32_data",
                          "int64_data", "string_data", "bool_data"):
                lst = getattr(tensor, field)
                if lst:
                    counts.append(f"{len(lst)} {field.replace('_data', '')}")
            if tensor.raw_data:
                counts.append(f"{len(tensor.raw_data)}B raw")
        payload = "  " + _dim(", ".join(counts)) if counts else ""
        lines.append(f"  {_cyan(entry.id): <24} {t}{payload}")
    return lines


def _inspect_functions(model) -> list[str]:
    if not model.functions:
        return []
    lines = [_section_header(f"User-defined Functions ({len(model.functions)})")]
    for fn in model.functions:
        params = ", ".join(
            f"{p.name}: {p.data_type.name}" for p in fn.parameters
        )
        ret = fn.result_data_type.name if fn.result_data_type.value != 0 else "?"
        lines.append(f"  {_cyan(fn.name)}({params}) → {ret}")
        if fn.doc_string:
            lines.append(f"    {_dim(fn.doc_string)}")
    return lines


def _inspect_verification(model) -> list[str]:
    v = model.verification
    if not v or not v.cases:
        return []
    lines = [_section_header(f"Verification ({len(v.cases)} case{'s' if len(v.cases) != 1 else ''})")]
    if v.tolerance:
        tol_parts = []
        if v.tolerance.atol is not None:
            tol_parts.append(f"atol={v.tolerance.atol}")
        if v.tolerance.rtol is not None:
            tol_parts.append(f"rtol={v.tolerance.rtol}")
        if tol_parts:
            lines.append(f"  {_dim('tolerance:'): <20} {', '.join(tol_parts)}")
    for i, case in enumerate(v.cases):
        desc = f"  {_dim('—')} {case.description}" if case.description else ""
        lines.append(f"  [{i}] inputs=[{', '.join(r.id for r in case.inputs)}]"
                     f"  expected=[{', '.join(r.id for r in case.expected_outputs)}]{desc}")
    return lines


def _inspect_warmup(model) -> list[str]:
    w = model.warmup
    if not w or not w.cases:
        return []
    lines = [_section_header(f"Warmup ({len(w.cases)} case{'s' if len(w.cases) != 1 else ''})")]
    for i, case in enumerate(w.cases):
        repeat = f"  ×{case.repeat}" if case.repeat and case.repeat > 1 else ""
        desc = f"  {_dim('—')} {case.description}" if case.description else ""
        lines.append(f"  [{i}] inputs=[{', '.join(r.id for r in case.inputs)}]{repeat}{desc}")
    return lines


def _inspect_sample_inputs(model) -> list[str]:
    s = model.sample_inputs
    if not s or not s.cases:
        return []
    lines = [_section_header(f"Sample Inputs ({len(s.cases)} case{'s' if len(s.cases) != 1 else ''})")]
    for i, case in enumerate(s.cases):
        desc = f"  {_dim('—')} {case.description}" if case.description else ""
        lines.append(f"  [{i}] inputs=[{', '.join(r.id for r in case.inputs)}]{desc}")
    return lines


_SECTION_RENDERERS = {
    "metadata":  _inspect_metadata,
    "imports":   _inspect_imports,
    "inputs":    _inspect_inputs,
    "outputs":   _inspect_outputs,
    "schema":    _inspect_schema,
    "nodes":     _inspect_nodes,
    "tensor_entries": _inspect_tensor_entries,
    "functions": _inspect_functions,
    "verification":   _inspect_verification,
    "warmup":         _inspect_warmup,
    "sample_inputs":  _inspect_sample_inputs,
}


def _cmd_inspect(args: argparse.Namespace) -> int:
    path = Path(args.file)
    model = _load_model(path)

    if args.json:
        json.dump(model.to_dict(), sys.stdout, indent=2, ensure_ascii=False)
        print()
        return 0

    sections = (
        [args.section] if args.section and args.section != "all"
        else list(_ALL_SECTIONS)
    )

    verbose = getattr(args, "verbose", False)

    print(_bold("OMLE Model") + f"  {_dim(str(path))}")
    print()

    for section in sections:
        renderer = _SECTION_RENDERERS.get(section)
        if renderer is None:
            print(f"Unknown section: {section!r}", file=sys.stderr)
            continue
        # Pass verbose flag only to node renderer
        if section == "nodes":
            block = renderer(model, verbose=verbose)
        else:
            block = renderer(model)

        if not block:
            continue
        print("\n".join(block))
        print()

    return 0


# ── convert subcommand ───────────────────────────────────────────────────────

def _cmd_convert(convert_args: list[str]) -> int:
    try:
        from omle_convert.cli import (
            _build_parser as _convert_build_parser,  # type: ignore[import]
        )
    except ImportError:
        print(
            "Error: omle-convert is not installed.\n"
            "Install it with:  pip install omle-convert",
            file=sys.stderr,
        )
        return 2

    parser = _convert_build_parser()
    parser.prog = "omle convert"
    for action in parser._actions:
        if hasattr(action, "choices") and isinstance(action.choices, dict):
            for name, subparser in action.choices.items():
                subparser.prog = f"omle convert {name}"

    # parse_args with subs.required=True errors before the version action fires.
    if convert_args and convert_args[0] in ("-V", "--version"):
        from omle_convert import __version__  # type: ignore[import]
        print(f"omle-convert {__version__}")
        return 0

    args = parser.parse_args(convert_args)
    try:
        args.func(args)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


# ── predict subcommand ───────────────────────────────────────────────────────

def _cmd_predict(predict_args: list[str]) -> int:
    """Forward to the omle-predict executable that omle-runtime installs.

    `convert` borrows a Python parser from its package; omle-predict is a
    native binary instead, so this hands argv over and returns its exit code.
    Locating the real tool rather than restating it here keeps one
    implementation, and one definition of the CSV formats it reads and writes.
    """
    exe = shutil.which("omle-predict")
    if exe is None:
        print(
            "Error: omle-predict is not installed.\n"
            "Install it with:  pip install omle-runtime",
            file=sys.stderr,
        )
        return 2

    return subprocess.call([exe, *predict_args])


# ── view subcommand ──────────────────────────────────────────────────────────

def _cmd_view(args: argparse.Namespace) -> int:
    try:
        from omle_viewer.cli import (
            main as _viewer_main,  # type: ignore[import]
        )
    except ImportError:
        print(
            "Error: omle-viewer is not installed.\n"
            "Install it with:  pip install omle-viewer",
            file=sys.stderr,
        )
        return 2

    sys.argv = ["omle-viewer", args.file]
    _viewer_main()
    return 0


# ── Argument parser ───────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    from omle import __version__
    parser = argparse.ArgumentParser(
        prog="omle",
        description="OMLE command-line tools",
    )
    parser.add_argument(
        "--version", "-V",
        action="version",
        version=f"omle {__version__}",
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")
    sub.required = True

    # ── convert ──────────────────────────────────────────────────────────────
    sub.add_parser(
        "convert",
        help="Convert an ML model to OMLE format (requires omle-convert)",
        add_help=False,
    )

    # ── predict ──────────────────────────────────────────────────────────────
    # add_help=False for the same reason as convert: -h belongs to the tool
    # being forwarded to, not to this parser.
    sub.add_parser(
        "predict",
        help="Score a model over a CSV of features (requires omle-runtime)",
        add_help=False,
    )

    # ── validate ─────────────────────────────────────────────────────────────
    p_val = sub.add_parser(
        "validate",
        help="Validate an OMLE model file",
        description=(
            "Load and validate an OMLE model file against structural rules "
            "and (optionally) the operator/function registries."
        ),
    )
    p_val.add_argument("file", metavar="FILE",
                       help="Path to the model file (.json or .omle)")
    p_val.add_argument(
        "--no-registry",
        action="store_true",
        default=False,
        help="Skip registry-based operator and function checks",
    )

    # ── view ─────────────────────────────────────────────────────────────────
    p_view = sub.add_parser(
        "view",
        help="Open an OMLE model in the interactive DAG viewer (requires omle-viewer)",
        description="Open an OMLE model file in the default web browser using the interactive DAG viewer.",
    )
    p_view.add_argument("file", metavar="FILE",
                        help="Path to the model file (.json or .omle)")

    # ── inspect ──────────────────────────────────────────────────────────────
    p_ins = sub.add_parser(
        "inspect",
        help="Inspect an OMLE model file",
        description="Display a human-readable summary of an OMLE model.",
    )
    p_ins.add_argument("file", metavar="FILE",
                       help="Path to the model file (.json or .omle)")
    p_ins.add_argument(
        "--section",
        metavar="SECTION",
        choices=list(_ALL_SECTIONS) + ["all"],
        default="all",
        help=(
            "Which section to show: "
            + ", ".join(_ALL_SECTIONS)
            + ", all (default: all)"
        ),
    )
    p_ins.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output the model as JSON instead of a human-readable summary",
    )
    p_ins.add_argument(
        "-v", "--verbose",
        action="store_true",
        default=False,
        help="Show additional detail (e.g. node attributes)",
    )

    return parser


# ── Entry point ───────────────────────────────────────────────────────────────

def main(argv: Optional[list[str]] = None) -> None:
    if argv is None:
        argv = sys.argv[1:]

    # Intercept the subcommands that delegate to another package before
    # building the normal parser, so that every argument (including --help and
    # flags) is forwarded verbatim to the tool that owns its own parser.
    if argv and argv[0] == "convert":
        sys.exit(_cmd_convert(argv[1:]))
    if argv and argv[0] == "predict":
        sys.exit(_cmd_predict(argv[1:]))

    parser = _build_parser()
    args = parser.parse_args(argv)

    handlers = {
        "validate": _cmd_validate,
        "inspect":  _cmd_inspect,
        "view":     _cmd_view,
    }
    handler = handlers.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(1)

    sys.exit(handler(args))


if __name__ == "__main__":
    main()
