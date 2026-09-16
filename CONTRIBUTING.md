# Contributing to OMLE

Thanks for your interest in OMLE. This document covers how to work on this
repository specifically — setup, the layout, and the checks that need to pass
before a change lands.

By participating you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).

## What lives here

This repository holds the **format** and its **Python reference implementation**:

- `protobuf/omle.proto` — the wire format
- `registries/` — the operator and function registries
- `spec/` — specification documents
- `src/omle/` — the Python SDK: IR types, protobuf I/O, validation, CLI

Everything else in the ecosystem has its own repository. Please open changes
against the repository that owns the code:

| Repository | Owns |
|---|---|
| [omle-convert](https://github.com/openmle/omle-convert) | Converters from trained models to `.omle` |
| [omle-runtime](https://github.com/openmle/omle-runtime) | C++ inference runtime, Python/Java bindings |
| [omle-viewer](https://github.com/openmle/omle-viewer) | Interactive DAG viewer |
| [omle.js](https://github.com/openmle/omle.js) | TypeScript loader and execution engine |

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate

# Upgrade pip first. The build requires setuptools>=77 via PEP 517, and older
# pip (macOS system Python ships 21.x) falls back to a legacy `setup.py develop`
# path that fails with "returned non-zero exit status 1".
python -m pip install --upgrade pip

pip install -e ".[dev]"
pytest tests/
```

The test suite is fast — the whole thing runs in well under a second, so run it
often. `pytest` works straight from a checkout even without installing, because
`pyproject.toml` puts `src/` on the path; be aware that this means a passing
`pytest` does **not** prove the package installs correctly.

## Repository layout

```
protobuf/omle.proto        the wire format
registries/
  operators/
    operators.json            base template: global metadata, rules, vocabulary
    namespaces/*.json         one file per operator namespace
    schema/*.json             JSON schemas for the above
  functions/                  same layout for expression functions
spec/                         specification documents
src/omle/                  the Python SDK
  ir/                         in-memory dataclasses
  proto/                      generated pb2 module + IR↔proto conversion
  validation.py               structural and registry validation
  registry.py                 registry loading
docs/                         GENERATED reference docs — do not hand-edit
tools/                        developer tools (see below)
tests/                        pytest suite
```

## Generated files — never hand-edit

| File | Produced by |
|---|---|
| `src/omle/proto/omle_pb2.py` | `scripts/gen_proto.sh` |
| `src/omle/_version.py` | setuptools-scm at build time (gitignored) |
| `docs/**/*.md` | `python tools/gen_docs.py` |
| `omle/registry/*.json` (in the built wheel) | `setup.py` at build time |

## Common tasks

### Changing the proto schema

1. Edit `protobuf/omle.proto`.
2. Regenerate the Python bindings: `bash scripts/gen_proto.sh` (needs `grpcio-tools`).
3. Update the matching IR dataclass in `src/omle/ir/` and the conversion in
   `src/omle/proto/convert.py` — the IR and the proto are maintained by hand
   in parallel, so a new field needs both sides plus `to_dict`/`from_dict`.
4. Add a round-trip test in `tests/test_proto_convert.py`.

### Changing the registries

Operators and functions are authored one file per namespace under
`registries/<kind>/namespaces/`, and merged with `registries/<kind>/<kind>.json`
into a single bundled JSON at build time.

1. Edit the namespace file.
2. Validate: `python tools/validate_registry.py` — exits non-zero on failure.
   It needs `jsonschema` (included in the `dev` extra); without it the JSON
   Schema checks are skipped with only a warning and everything appears to pass.
3. Regenerate and **commit** the docs: `python tools/gen_docs.py`. These are
   checked-in generated files; leaving them stale makes the published reference
   disagree with the registry.
4. If you added an operator, add a validation test in
   `tests/test_registry_validation.py`.

Keep registry diffs surgical. Editing these files by loading and re-dumping the
JSON reformats the whole file and buries a two-line change in hundreds of lines
of noise — edit the text directly.

New attribute types and input kinds must be added in three places or validation
will reject them: the vocabulary in `registries/<kind>/<kind>.json`, the enum in
`registries/<kind>/schema/*.schema.json`, and the checker in
`tools/validate_registry.py`.

### Changing validation rules

Validation lives in `src/omle/validation.py`. When adding a rule, prefer
reporting an error over raising — `validate()` returns a `ValidationResult` and
is expected not to throw on malformed input. Note that IR fields typed as
`Scalar` need unwrapping via `.value` before numeric comparison.

Document user-visible rules in `spec/validation-rules.md`.

## Code style

| Files | Standard | Enforced by |
|---|---|---|
| `*.py` | [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) | `ruff check .` |
| `*.proto` | [Google Protocol Buffers Style Guide](https://protobuf.dev/programming-guides/style/) | review (2-space indent, no tabs) |

Run `ruff check .` before pushing; `ruff check --fix .` handles most findings.
Configuration lives in `[tool.ruff]` in `pyproject.toml`, and CI runs it on
every push.

Two deliberate notes on how far the enforcement goes:

- **No autoformatter.** `ruff format` would rewrite the aligned dict literals
  and `# ── section ──` dividers this codebase uses. The linter is configured
  to leave that alignment alone.
- **Style rules are adopted in stages.** Correctness, imports, naming and
  bugbear rules are enforced and currently clean. Two groups are not yet
  enabled, because the codebase is not clean against them:
  `E501` line length at Google's 80 columns (394 lines over), and `D`
  docstring conventions (391 findings). New code should follow both anyway;
  they will be switched on as the backlog is cleared.

## Pre-commit hooks (optional)

```bash
pip install pre-commit
pre-commit install
```

`.pre-commit-config.yaml` wires up basic hygiene plus three repo-specific gates:
registry validation, a check that `docs/` still matches the registries, and the
test suite. Run them over the whole tree at any time with
`pre-commit run --all-files`.

The hooks call `python` and `pytest` directly, so activate the dev environment
first. Nothing here is required — CI enforces the same things — but it catches
a stale `docs/` before review rather than after.

## Tests and CI

`.github/workflows/test.yml` runs `pytest` on Python 3.10 through 3.14 for every
push and pull request. `.github/workflows/publish.yml` additionally runs the
suite against the *built wheel* before publishing, which catches packaging
problems that a source-tree test run cannot.

Please add a test with any behaviour change. If you are fixing a bug, a test
that fails before your fix is the most useful thing you can include.

## Versioning and compatibility

The format is **pre-1.0** and stabilizing toward v1:

- `ModelMetadata.format_version` is `0.1.0`
- Operator and function namespaces are at version `0.1`

Until v1, MINOR bumps may include breaking changes. Additive changes — new
optional proto fields, new operators, new functions — are preferred over
changes to existing semantics. If a change alters what an existing valid model
means, say so explicitly in the pull request.

Changes here ripple outward: the converters emit what this repo defines, and the
runtimes consume it. If your change affects the wire format or an operator
contract, note which ecosystem repositories need a matching update.

## Releases

Releases are tag-driven. Pushing a `v*` tag runs `.github/workflows/publish.yml`,
which builds, verifies the wheel in a clean environment, and publishes to PyPI
via Trusted Publishing. Version numbers come from the git tag through
setuptools-scm — there is no version string to bump by hand.

## Reporting bugs

Please include the OMLE version, how the model was produced (converter and
source framework, if any), and the smallest model file or script that shows the
problem. For validation failures, the full output of
`omle validate <file>` is the most useful thing to paste.

## License

Contributions are accepted under the [Apache License 2.0](LICENSE), in
accordance with section 5 of that license. There is no separate CLA.
