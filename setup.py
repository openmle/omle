"""Custom build steps for the omle package.

1. Proto compilation
   Compiles ``protobuf/omle.proto`` → ``src/omle/proto/omle_pb2.py``
   using ``grpc_tools.protoc`` (installed via the ``dev`` extra).  The generated
   file is written into the source tree so editable installs and wheel builds
   both pick it up without needing a separate code-gen step.

2. Registry merge
   Merges per-namespace JSON files under ``registries/`` into bundled package
   JSON files placed at ``omle/registry/`` inside the build output.

   Source layout (never committed under src/):
     registries/
       operators/
         operators.json             ← base template (global metadata, empty namespaces)
         namespaces/
           omle.core.json
           omle.feature.json
           ...
         schema/
           operators.schema.json
           operators.namespace.schema.json
       functions/
         functions.json             ← base template (global metadata, empty namespaces)
         namespaces/
           omle.functions.json
           ...
         schema/
           functions.schema.json
           functions.namespace.schema.json

   Build output (inside wheel / editable install):
     omle/registry/
       operators.json               ← merged (base + all namespace files)
       functions.json               ← merged (base + all namespace files)
       operators.schema.json
       operators.namespace.schema.json
       functions.schema.json
       functions.namespace.schema.json
"""

import json
import shutil
import subprocess
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py


def _compile_proto(root: Path) -> None:
    """Compile protobuf/omle.proto → src/omle/proto/omle_pb2.py."""
    proto_file = root / "protobuf" / "omle.proto"
    if not proto_file.exists():
        return
    out_dir = root / "src" / "omle" / "proto"
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        from grpc_tools import protoc  # type: ignore[import]
        ret = protoc.main([
            "grpc_tools.protoc",
            f"--proto_path={proto_file.parent}",
            f"--python_out={out_dir}",
            str(proto_file.name),
        ])
        if ret != 0:
            raise RuntimeError(f"protoc exited with code {ret}")
    except ImportError:
        # Fall back to the system protoc binary when grpcio-tools is not installed.
        ret = subprocess.call([
            "protoc",
            f"--proto_path={proto_file.parent}",
            f"--python_out={out_dir}",
            str(proto_file.name),
        ])
        if ret != 0:
            raise RuntimeError(
                "Neither grpcio-tools nor the system protoc binary is available. "
                "Install grpcio-tools: pip install grpcio-tools"
            ) from None


def _merge_registry(base_path: Path, ns_dir: Path) -> dict:
    """Return a registry dict with namespace files merged into base."""
    with open(base_path, encoding="utf-8") as f:
        data = json.load(f)
    namespaces = []
    if ns_dir.is_dir():
        for ns_file in sorted(ns_dir.glob("*.json")):
            with open(ns_file, encoding="utf-8") as f:
                namespaces.append(json.load(f))
    data["namespaces"] = namespaces
    return data


class BuildPyWithRegistry(build_py):
    def run(self):
        _compile_proto(Path(__file__).parent)
        super().run()
        self._build_registry()

    def editable_mode_shim(self, *args, **kwargs):
        # Called by some editable-install paths; run codegen so dev imports work too.
        _compile_proto(Path(__file__).parent)
        result = super().editable_mode_shim(*args, **kwargs)
        self._build_registry()
        return result

    def _build_registry(self):
        root = Path(__file__).parent / "registries"
        if not root.is_dir():
            return

        dst = Path(self.build_lib) / "omle" / "registry"
        dst.mkdir(parents=True, exist_ok=True)

        for kind in ("operators", "functions"):
            kind_dir = root / kind
            if not kind_dir.is_dir():
                continue

            # Merge base template + per-namespace files → single JSON
            base = kind_dir / f"{kind}.json"
            if not base.exists():
                raise RuntimeError(f"Missing registry base template: {base}")
            merged = _merge_registry(base, kind_dir / "namespaces")
            out = dst / f"{kind}.json"
            with open(out, "w", encoding="utf-8") as f:
                json.dump(merged, f, indent=2)

            # Copy schema files alongside the merged JSON
            schema_dir = kind_dir / "schema"
            if schema_dir.is_dir():
                for schema_file in schema_dir.glob("*.json"):
                    shutil.copy2(schema_file, dst / schema_file.name)


setup(cmdclass={"build_py": BuildPyWithRegistry})
