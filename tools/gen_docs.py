"""Developer tool: generate Markdown reference docs from the OMLE registries.

Usage::

    python tools/gen_docs.py
    python tools/gen_docs.py --out-dir path/to/docs
    python tools/gen_docs.py --operators-file path/to/operators.v1.json
    python tools/gen_docs.py --functions-file path/to/functions.v1.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# Allow running directly from the repo root without installing the package.
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

_RESET = "\033[0m"
_BOLD  = "\033[1m"
_DIM   = "\033[2m"


def _c(text: str, code: str) -> str:
    return f"{code}{text}{_RESET}" if sys.stdout.isatty() else text


def _bold(t: str) -> str: return _c(t, _BOLD)
def _dim(t: str)  -> str: return _c(t, _DIM)


# ── Markdown helpers ──────────────────────────────────────────────────────────

def _anchor(text: str) -> str:
    return text.lower().replace(" ", "-").replace(".", "").replace("(", "").replace(")", "")


def _fmt_inputs_table(inputs: list[dict]) -> list[str]:
    if not inputs:
        return ["_(none)_", ""]
    has_constraints = any(i.get("shape_constraints") for i in inputs)
    header = "| Name | Required | Variadic | Kind(s) |"
    rule = "|------|----------|----------|---------|"
    if has_constraints:
        header += " Shape Constraints |"
        rule += "-------------------|"
    lines = [header, rule]
    for inp in inputs:
        name = inp.get("name", "")
        req = "yes" if inp.get("required", True) else "no"
        var = "yes" if inp.get("variadic", False) else "no"
        kinds = ", ".join(inp.get("kinds", []))
        row = f"| `{name}` | {req} | {var} | {kinds} |"
        if has_constraints:
            row += " " + "; ".join(inp.get("shape_constraints", [])) + " |"
        lines.append(row)
    return lines + [""]


def _fmt_outputs_table(outputs: list[dict]) -> list[str]:
    if not outputs:
        return ["_(none)_", ""]
    has_domain = any(o.get("domain_rule") for o in outputs)
    header = "| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |"
    rule = "|------|-----------|------------|--------------------|-----------|"
    if has_domain:
        header += " Domain Rule |"
        rule += "-------------|"
    lines = [header, rule]
    for out in outputs:
        name = out.get("name", "")
        tr = out.get("type_rule", "")
        sr = out.get("shape_rule", "")
        ml = out.get("measure_level_rule", "")
        rr = out.get("role_rule", "")
        row = f"| `{name}` | {tr} | {sr} | {ml} | {rr} |"
        if has_domain:
            row += f" {out.get('domain_rule', '')} |"
        lines.append(row)
    return lines + [""]


def _fmt_attributes_table(attrs: list[dict]) -> list[str]:
    if not attrs:
        return ["_(none)_", ""]
    has_desc = any(a.get("description") for a in attrs)
    header = "| Name | Type | Required | Default | Enum Values |"
    rule = "|------|------|----------|---------|-------------|"
    if has_desc:
        header += " Description |"
        rule += "-------------|"
    lines = [header, rule]
    for a in attrs:
        name = a.get("name", "")
        t = a.get("type", "")
        req = "yes" if a.get("required", False) else "no"
        default = str(a["default"]) if "default" in a else ""
        enums = ", ".join(f"`{v}`" for v in a.get("enum_values", []))
        row = f"| `{name}` | {t} | {req} | {default} | {enums} |"
        if has_desc:
            row += f" {a.get('description', '')} |"
        lines.append(row)
    return lines + [""]


# ── Operator namespace doc ────────────────────────────────────────────────────

def _generate_operator_namespace_doc(ns: dict) -> str:
    ns_name = ns.get("name", "")
    version = ns.get("version", "")
    description = ns.get("description", "")
    operators = ns.get("operators", [])

    lines: list[str] = []
    lines.append(f"# {ns_name} — Operators")
    lines.append("")
    if description:
        lines.append(f"_{description}_")
        lines.append("")
    if version:
        lines.append(f"**Registry version:** {version}")
        lines.append("")

    if operators:
        lines.append("## Operators")
        lines.append("")
        lines.append("| Operator | Category | Kind | Summary |")
        lines.append("|----------|----------|------|---------|")
        for op in operators:
            name = op.get("name", "")
            cat = op.get("category", "")
            kind = op.get("kind", "")
            summary = op.get("summary", "")
            anchor = _anchor(name)
            lines.append(f"| [`{name}`](#{anchor}) | {cat} | {kind} | {summary} |")
        lines.append("")
        lines.append("---")
        lines.append("")

    for op in operators:
        name = op.get("name", "")
        kind = op.get("kind", "")
        category = op.get("category", "")
        since = op.get("since", "")
        summary = op.get("summary", "")
        description = op.get("description", "") or op.get("doc", "")
        body_type = op.get("body_type")
        inputs = op.get("inputs", [])
        outputs = op.get("outputs", [])
        attrs = op.get("attributes", [])
        val_rules = op.get("validation_rules", [])
        converter_notes = op.get("converter_notes", [])

        lines.append(f"## {name}")
        lines.append("")
        meta_parts = []
        if category:
            meta_parts.append(f"**Category:** {category}")
        if since:
            meta_parts.append(f"**Since:** {since}")
        meta_parts.append(f"**Kind:** {kind}")
        if body_type:
            meta_parts.append(f"**Body type:** `{body_type}`")
        lines.append("  ·  ".join(meta_parts))
        lines.append("")
        lines.append(summary)
        lines.append("")
        if description:
            lines.append(description)
            lines.append("")

        lines.append("### Inputs")
        lines.append("")
        lines.extend(_fmt_inputs_table(inputs))

        lines.append("### Outputs")
        lines.append("")
        lines.extend(_fmt_outputs_table(outputs))

        lines.append("### Attributes")
        lines.append("")
        lines.extend(_fmt_attributes_table(attrs))

        if val_rules:
            lines.append("### Validation Rules")
            lines.append("")
            for rule in val_rules:
                lines.append(f"- {rule}")
            lines.append("")

        if converter_notes:
            lines.append("### Converter Notes")
            lines.append("")
            for note in converter_notes:
                lines.append(f"- {note}")
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


# ── Function namespace doc ────────────────────────────────────────────────────

def _generate_function_namespace_doc(ns: dict) -> str:
    ns_name = ns.get("name", "")
    version = ns.get("version", "")
    description = ns.get("description", "")
    functions = ns.get("functions", [])

    lines: list[str] = []
    lines.append(f"# {ns_name} — Functions")
    lines.append("")
    if description:
        lines.append(f"_{description}_")
        lines.append("")
    if version:
        lines.append(f"**Registry version:** {version}")
        lines.append("")

    if functions:
        lines.append("## Functions")
        lines.append("")
        lines.append("| Function | Category | Summary |")
        lines.append("|----------|----------|---------|")
        for fn in functions:
            name = fn.get("name", "")
            cat = fn.get("category", "")
            summary = fn.get("summary", "")
            anchor = _anchor(name)
            lines.append(f"| [`{name}`](#{anchor}) | {cat} | {summary} |")
        lines.append("")
        lines.append("---")
        lines.append("")

    for fn in functions:
        name = fn.get("name", "")
        category = fn.get("category", "")
        since = fn.get("since", "")
        summary = fn.get("summary", "")
        description = fn.get("description", "")
        args = fn.get("arguments", [])
        opt_params = fn.get("optional_parameters", [])
        returns = fn.get("returns", {})
        null_rule = fn.get("null_rule", "")
        notes = fn.get("notes", [])

        lines.append(f"## {name}")
        lines.append("")
        meta_parts = []
        if category:
            meta_parts.append(f"**Category:** {category}")
        if since:
            meta_parts.append(f"**Since:** {since}")
        if null_rule:
            meta_parts.append(f"**Null rule:** {null_rule}")
        if meta_parts:
            lines.append("  ·  ".join(meta_parts))
            lines.append("")
        lines.append(summary)
        lines.append("")
        if description:
            lines.append(description)
            lines.append("")

        sig_parts = []
        for arg in args:
            aname = arg.get("name", "")
            sig_parts.append(f"*{aname}..." if arg.get("variadic", False) else f"*{aname}*")
        for p in opt_params:
            sig_parts.append(f"[{p.get('name', '')}=...]")
        lines.append("```")
        lines.append(f"{name}({', '.join(sig_parts)})")
        lines.append("```")
        lines.append("")

        if args:
            lines.append("### Arguments")
            lines.append("")
            lines.append("| Name | Kind(s) | Variadic |")
            lines.append("|------|---------|----------|")
            for arg in args:
                aname = arg.get("name", "")
                kinds = ", ".join(arg.get("kinds", []))
                var = "yes" if arg.get("variadic", False) else "no"
                lines.append(f"| `{aname}` | {kinds} | {var} |")
            lines.append("")

        if opt_params:
            lines.append("### Optional Parameters")
            lines.append("")
            lines.append("| Name | Kind(s) |")
            lines.append("|------|---------|")
            for p in opt_params:
                pname = p.get("name", "")
                kinds = ", ".join(p.get("kinds", []))
                lines.append(f"| `{pname}` | {kinds} |")
            lines.append("")

        if returns:
            lines.append("### Returns")
            lines.append("")
            tr = returns.get("type_rule", "")
            ml = returns.get("measure_level_rule", "")
            if tr:
                lines.append(f"- **Type:** {tr}")
            if ml:
                lines.append(f"- **Measure level:** {ml}")
            lines.append("")

        if notes:
            lines.append("### Notes")
            lines.append("")
            for note in notes:
                lines.append(f"- {note}")
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


# ── Index ─────────────────────────────────────────────────────────────────────

def _generate_index(op_namespaces: list[dict], fn_namespaces: list[dict],
                    registry_version: str = "1.0") -> str:
    lines = [
        "# OMLE Registry Reference",
        "",
        f"_Registry version {registry_version}_",
        "",
    ]

    def _entry(ns: dict) -> str:
        name = ns.get("name", "")
        ops = ns.get("operators", [])
        structured = sum(1 for o in ops if o.get("kind") == "structured")
        detail = f"{len(ops)} operators"
        if structured:
            detail += f", {structured} with a dedicated proto body"
        return f"- [`{name}`](operators/{name}.md) — {ns.get('description', '')} ({detail})"

    # The ML namespace is the model surface: each operator is a trained model
    # family. The rest describe the data path around it.
    ml = [ns for ns in op_namespaces if ns.get("name") == "omle.ml"]
    rest = [ns for ns in op_namespaces if ns.get("name") != "omle.ml"]

    if ml:
        lines += [
            "## ML Model Operators",
            "",
            "Trained model families. Operators of kind `structured` carry a dedicated",
            "protobuf message that preserves the model's own semantics; generic ones",
            "carry their parameters as typed attributes.",
            "",
        ]
        lines += [_entry(ns) for ns in ml]
        lines.append("")

    if rest:
        lines += [
            "## Feature and Graph Operators",
            "",
            "Everything around the model: preprocessing before it, and aggregation,",
            "voting and score selection after it.",
            "",
        ]
        lines += [_entry(ns) for ns in rest]
        lines.append("")

    lines.append("## Function Namespaces")
    lines.append("")
    for ns in fn_namespaces:
        name = ns.get("name", "")
        desc = ns.get("description", "")
        fns = ns.get("functions", [])
        lines.append(f"- [`{name}`](functions/{name}.md) — {desc} ({len(fns)} functions)")
    lines.append("")
    return "\n".join(lines)


# ── Core generation ───────────────────────────────────────────────────────────

def _load_registry_data(kind: str, explicit_path: Optional[Path]) -> dict:
    from omle.registry import _REGISTRY_DIR, _merge_registry_data

    if explicit_path is not None:
        with open(explicit_path, encoding="utf-8") as f:
            return json.load(f)
    bundled = _REGISTRY_DIR / f"{kind}.v1.json"
    if bundled.exists():
        with open(bundled, encoding="utf-8") as f:
            return json.load(f)
    return _merge_registry_data(kind)


def generate_docs(
    out_dir: Path,
    operators_path: Optional[Path] = None,
    functions_path: Optional[Path] = None,
) -> list[Path]:
    op_data = _load_registry_data("operators", operators_path)
    fn_data = _load_registry_data("functions", functions_path)

    op_ns_list: list[dict] = op_data.get("namespaces", [])
    fn_ns_list: list[dict] = fn_data.get("namespaces", [])
    registry_version: str = op_data.get("registry_version", "1.0")

    written: list[Path] = []

    op_dir = out_dir / "operators"
    op_dir.mkdir(parents=True, exist_ok=True)
    for ns in op_ns_list:
        name = ns.get("name", "unknown")
        p = op_dir / f"{name}.md"
        p.write_text(_generate_operator_namespace_doc(ns), encoding="utf-8")
        written.append(p)

    fn_dir = out_dir / "functions"
    fn_dir.mkdir(parents=True, exist_ok=True)
    for ns in fn_ns_list:
        name = ns.get("name", "unknown")
        p = fn_dir / f"{name}.md"
        p.write_text(_generate_function_namespace_doc(ns), encoding="utf-8")
        written.append(p)

    index_path = out_dir / "README.md"
    index_path.write_text(_generate_index(op_ns_list, fn_ns_list, registry_version),
                          encoding="utf-8")
    written.append(index_path)

    return written


# ── Entry point ───────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="gen_docs",
        description=(
            "Generate per-namespace Markdown reference pages from the operator "
            "and function registries, plus a README.md."
        ),
    )
    parser.add_argument(
        "--out-dir",
        metavar="DIR",
        default="docs",
        help="Output directory (default: docs)",
    )
    parser.add_argument(
        "--operators-file",
        metavar="FILE",
        default=None,
        help="Path to operators registry JSON (default: bundled registry/operators.v1.json)",
    )
    parser.add_argument(
        "--functions-file",
        metavar="FILE",
        default=None,
        help="Path to functions registry JSON (default: bundled registry/functions.v1.json)",
    )
    args = parser.parse_args(argv)

    out_dir = Path(args.out_dir)
    op_path = Path(args.operators_file) if args.operators_file else None
    fn_path = Path(args.functions_file) if args.functions_file else None

    try:
        written = generate_docs(out_dir, op_path, fn_path)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error generating docs: {e}", file=sys.stderr)
        sys.exit(2)

    n = len(written)
    print(_bold(f"Generated {n} file{'s' if n != 1 else ''}") + f"  {_dim(str(out_dir))}")
    for p in written:
        rel = p.relative_to(out_dir) if p.is_relative_to(out_dir) else p
        print(f"  {_dim('→')} {rel}")
    sys.exit(0)


if __name__ == "__main__":
    main()
