"""The three version axes stay separate, and their sources stay single.

OMLE versions three things independently:

  * the schema      — ``omle.FORMAT_VERSION``, describing omle.proto
  * operator sets   — one version per namespace, declared in the registries
  * this package    — ``omle.__version__``, from setuptools-scm

The failure these tests exist to catch is not a wrong number but a duplicated
one: a second copy of the schema version that a bump forgets, or a namespace
version transcribed into a producer. Both have happened, and both are invisible
until a model is written with a version that never described it.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import omle
from omle._format import (
    FORMAT_VERSION,
    is_supported_format,
    parse_format_version,
)
from omle.ir.verification import (
    ModelVerification,
    TensorRef,
    VerificationCase,
)
from omle.registry import namespace_versions

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "src" / "omle"


# ── The schema version has exactly one definition ────────────────────────────

def test_format_version_is_wellformed():
    assert parse_format_version(FORMAT_VERSION) is not None, FORMAT_VERSION


def test_metadata_default_comes_from_the_constant():
    # Not merely equal to "0.1.0": equal to whatever the constant now says, so
    # bumping the constant cannot leave the dataclass default behind.
    assert omle.ModelMetadata().format_version == FORMAT_VERSION
    assert omle.ModelMetadata.from_dict({}).format_version == FORMAT_VERSION


def test_no_hardcoded_schema_version_outside_the_constant():
    """No module re-states the schema version as a literal.

    A literal here is how the four copies this consolidated came about: the
    dataclass default, the from_dict fallback, the package docstring, and a
    fourth in omle-convert. Each was correct when written.
    """
    pattern = re.compile(r"""format_version\s*[=:]\s*["']\d+\.\d+""")
    offenders = []
    for path in sorted(SRC.rglob("*.py")):
        if path.name in {"_format.py", "_version.py"} or "proto/omle_pb2" in str(path):
            continue
        for lineno, line in enumerate(path.read_text().splitlines(), 1):
            if pattern.search(line):
                offenders.append(f"{path.relative_to(REPO)}:{lineno}: {line.strip()}")
    assert not offenders, (
        "schema version written as a literal; use omle.FORMAT_VERSION:\n  "
        + "\n  ".join(offenders)
    )


# ── Schema version is independent of the package version ─────────────────────

def test_schema_version_bump_is_deliberate():
    """A tripwire, not a property: the schema version is pinned here too.

    The point of separating the axes is that releasing this package never moves
    the schema version. Nothing else would notice if it did, so this asserts the
    literal — failing here means either a genuine schema change, in which case
    update this line and the sibling constants it guards, or an accident.
    """
    assert FORMAT_VERSION == "0.1.0"


def test_package_version_is_a_separate_axis():
    """The package version must not be the source of the schema version."""
    pkg = getattr(omle, "__version__", None)
    if pkg is None:  # a checkout with no generated _version.py
        pytest.skip("package version unavailable")
    # Parsed rather than grepped: the module's docstring names __version__ on
    # purpose, to explain the distinction. Only real imports count.
    import ast

    tree = ast.parse((SRC / "_format.py").read_text())
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    forbidden = {"importlib.metadata", "importlib", "setuptools_scm",
                 "omle", "omle._version"}
    assert not (imported & forbidden), (
        f"_format.py imports {sorted(imported & forbidden)}; the schema version "
        "must be a literal, not derived from the package version"
    )


# ── Operator-set versions come from the registries ───────────────────────────

def test_namespace_versions_cover_the_registry_namespaces():
    versions = namespace_versions()
    assert versions, "no namespace versions found; is the registry missing?"
    # Every namespace the operator registry knows about must have a version, or
    # a producer writing operator_imports has nothing to record.
    for ns in omle.registry.get_operator_registry().namespaces:
        assert ns in versions, f"{ns} has no declared version"
    for ns, ver in versions.items():
        assert parse_format_version(ver) is not None, f"{ns}: bad version {ver!r}"


def test_namespace_versions_match_the_registry_files():
    """The function reports what the JSON declares, not a transcription."""
    import json

    expected = {}
    for kind in ("operators", "functions"):
        ns_dir = REPO / "registries" / kind / "namespaces"
        for f in sorted(ns_dir.glob("*.json")):
            d = json.loads(f.read_text())
            expected[d["name"]] = str(d["version"])
    assert namespace_versions() == expected


# ── The compatibility rule the proto documents ───────────────────────────────

@pytest.mark.parametrize("version", ["0.1.0", "0.1", "0.1.9", ""])
def test_supported_versions(version):
    assert is_supported_format(version)


@pytest.mark.parametrize("version", ["0.2.0", "0.0.1", "1.0.0", "2.0.0"])
def test_unsupported_versions(version):
    # Pre-1.0 requires an exact MINOR match: omle.proto says 0.x MINOR bumps may
    # still break compatibility.
    assert not is_supported_format(version)


@pytest.mark.parametrize("version", ["abc", "0.1.x", "0..1", "0.1.", ".1", "0.1.2.3"])
def test_malformed_versions_are_unsupported(version):
    assert parse_format_version(version) is None
    assert not is_supported_format(version)


def _model(fv, verification=None):
    return omle.OMLEModel(
        metadata=omle.ModelMetadata(format_version=fv, name="m"),
        inputs=[omle.InputSpec(
            name="X",
            type=omle.TensorType(dtype=omle.DataType.FLOAT32, shape=[-1, 1]))],
        outputs=[omle.OutputSpec(name="y", role=omle.OutputRole.PREDICTION)],
        verification=verification,
    )


def _fv(kind, fv, **kw):
    res = omle.validate(_model(fv, **kw))
    return [x for x in getattr(res, kind) if "format_version" in str(x)]


def test_unsupported_version_is_an_advisory_not_an_error():
    """An unreadable schema version does not make the document invalid.

    Whether a consumer can execute the model is settled at load time by its
    verification cases. A static validator cannot run those, so it says what it
    knows and leaves is_valid alone.
    """
    assert not _fv("errors", "0.2.0")
    assert _fv("warnings", "0.2.0"), "a newer MINOR should be flagged while pre-1.0"
    assert _fv("warnings", "9.0.0"), "an unknown MAJOR should be flagged"
    # The advisory must not change validity at all. Comparing the error lists
    # for a supported and an unsupported version is the precise claim; asserting
    # is_valid would instead depend on the rest of this stub model being sound.
    assert ([str(e) for e in omle.validate(_model("0.2.0")).errors]
            == [str(e) for e in omle.validate(_model(FORMAT_VERSION)).errors]), (
        "the declared version must not add or remove validation errors"
    )


def test_verification_cases_silence_the_version_advisory():
    """A model that can prove itself at load time is not second-guessed here."""
    verif = ModelVerification(cases=[VerificationCase(
        inputs=[TensorRef(id="in")],
        expected_outputs=[TensorRef(id="out")],
    )])
    assert not _fv("warnings", "0.2.0", verification=verif)
    assert not _fv("errors", "0.2.0", verification=verif)


def test_malformed_and_missing_versions_stay_errors():
    """Well-formedness is this validator's job, and it is unambiguous."""
    assert _fv("errors", "nonsense"), "a malformed version is a schema violation"
    assert _fv("errors", ""), "an empty version is a schema violation"
    # Even with verification cases: the field itself is invalid.
    verif = ModelVerification(cases=[VerificationCase(
        inputs=[TensorRef(id="in")],
        expected_outputs=[TensorRef(id="out")],
    )])
    assert _fv("errors", "nonsense", verification=verif)


def test_supported_version_is_clean():
    assert not _fv("errors", FORMAT_VERSION)
    assert not _fv("warnings", FORMAT_VERSION)


# ── The C++ runtime carries the same numbers ─────────────────────────────────

def test_runtime_constants_match_the_schema_version():
    """omle-runtime hardcodes the supported version in C++; keep it in step.

    It cannot import this constant, so the copy is unavoidable — but it does not
    have to be silent. Skipped when the sibling checkout is absent, since that
    is the normal case for an installed package.
    """
    loader = REPO.parent / "omle-runtime" / "src" / "graph_loader.cpp"
    if not loader.is_file():
        pytest.skip("omle-runtime checkout not present")

    text = loader.read_text()
    major = re.search(r"constexpr int kFormatMajor = (\d+);", text)
    minor = re.search(r"constexpr int kFormatMinor = (\d+);", text)
    assert major and minor, "kFormatMajor/kFormatMinor not found in graph_loader.cpp"

    want = parse_format_version(FORMAT_VERSION)
    assert want is not None
    got = (int(major.group(1)), int(minor.group(1)))
    assert got == want[:2], (
        f"omle-runtime supports {got[0]}.{got[1]}.x but the schema version is "
        f"{FORMAT_VERSION}; update kFormatMajor/kFormatMinor in "
        "omle-runtime/src/graph_loader.cpp"
    )
