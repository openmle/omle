"""The OMLE schema version, and the compatibility rule for reading it.

This is the one place the schema version is written down. It is deliberately a
literal rather than the package version: the two track different things, and
coupling them is the mistake this module exists to prevent.

  * ``FORMAT_VERSION`` describes ``omle.proto`` — the wire format. It moves when
    the schema changes, and stays put through any number of releases that only
    touch Python code.

  * The package version (``omle.__version__``, from setuptools-scm) describes
    this library, and belongs in ``ModelMetadata.producer_version``.

  * Operator sets are versioned separately again, per namespace, in the
    registries. See ``omle.registry.namespace_versions()``.

A leaf module with no omle imports, so ``ir.metadata`` and ``validation`` can
both use it without an import cycle.
"""

from __future__ import annotations

from typing import Optional, Tuple

# The schema version this library reads and writes. Bump on omle.proto changes
# only: MAJOR for wire-incompatible ones, MINOR for additive fields, PATCH for
# clarifications. Adding an operator bumps its namespace in the registry
# instead, leaving this alone.
FORMAT_VERSION = "0.1.0"


def parse_format_version(value: str) -> Optional[Tuple[int, int, int]]:
    """Return ``(major, minor, patch)``, or None if *value* is not parseable.

    Trailing components may be omitted, so "0.1" reads as (0, 1, 0). Anything
    that is not a dotted run of integers returns None rather than raising: the
    caller decides whether an unreadable version is an error, and for a
    validator that is a diagnostic rather than a crash.
    """
    if not value:
        return None
    parts = value.strip().split(".")
    if len(parts) > 3:
        return None
    nums = []
    for p in parts:
        if not p.isdigit():
            return None
        nums.append(int(p))
    while len(nums) < 3:
        nums.append(0)
    return (nums[0], nums[1], nums[2])


def is_supported_format(value: str) -> bool:
    """Whether a model declaring *value* is safe for this library to read.

    The rule the proto documents: a consumer must reject a MAJOR it does not
    support, and within a supported MAJOR may accept newer MINOR/PATCH when it
    can ignore unknown fields.

    Before 1.0 that is tightened to require an exact MINOR match, because the
    schema says outright that MINOR bumps may still break compatibility while
    the format is pre-1.0. Being lenient there would mean accepting a 0.2 model
    on the strength of a promise 0.x does not make.

    An empty version is accepted. Models built by hand and by the runtime's own
    tests carry no metadata at all, and refusing those would turn a missing
    descriptive field into a load failure.
    """
    if not value:
        return True
    v = parse_format_version(value)
    if v is None:
        return False
    cur = parse_format_version(FORMAT_VERSION)
    assert cur is not None, "FORMAT_VERSION must be parseable"
    if v[0] != cur[0]:
        return False
    if cur[0] == 0:
        return v[1] == cur[1]
    return True
