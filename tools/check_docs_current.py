"""Developer tool: verify docs/reference/ matches what the registries generate.

``docs/reference/`` is generated from ``registries/`` by ``tools/gen_docs.py``
and checked into the repository; the rest of ``docs/`` is written by hand. This
tool regenerates the reference into a temporary directory and compares, so a
stale reference is caught before it is committed rather than after it is
published.

Exits 0 when docs/ is current, 1 when it is stale (listing the files that
differ), leaving the checked-in docs untouched either way.

Usage::

    python tools/check_docs_current.py
"""

from __future__ import annotations

import filecmp
import subprocess
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
# Only the generated subtree. docs/ also holds hand-written pages — the index,
# the composite-scoping and validation-rules documents — and this check compares
# the union of generated and committed files, so pointing it at docs/ would
# report every hand-written page as stale.
_DOCS = _ROOT / "docs" / "reference"


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        proc = subprocess.run(
            [sys.executable, str(_ROOT / "tools" / "gen_docs.py"), "--out-dir", tmp],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            print("gen_docs.py failed:", file=sys.stderr)
            print(proc.stdout + proc.stderr, file=sys.stderr)
            return 1

        generated = {
            p.relative_to(tmp): p for p in Path(tmp).rglob("*.md")
        }
        committed = {
            p.relative_to(_DOCS): p for p in _DOCS.rglob("*.md")
        } if _DOCS.is_dir() else {}

        stale = sorted(
            str(rel) for rel in generated.keys() | committed.keys()
            if rel not in generated
            or rel not in committed
            or not filecmp.cmp(generated[rel], committed[rel], shallow=False)
        )

    if stale:
        print("docs/reference/ is out of date with registries/:", file=sys.stderr)
        for rel in stale:
            print(f"  docs/reference/{rel}", file=sys.stderr)
        print("\nRegenerate and stage them:  python tools/gen_docs.py", file=sys.stderr)
        return 1

    print(f"docs/reference/ is current ({len(committed)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
