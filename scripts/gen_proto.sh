#!/usr/bin/env bash
# Generate omle_pb2.py from the OMLE proto definition.
#
# Requirements:
#   pip install grpcio-tools
#
# Usage:
#   bash scripts/gen_proto.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROTO_FILE="$SCRIPT_DIR/../protobuf/omle.proto"
OUT_DIR="$SCRIPT_DIR/../src/omle/proto"

python -m grpc_tools.protoc \
  -I"$(dirname "$PROTO_FILE")" \
  --python_out="$OUT_DIR" \
  "$PROTO_FILE"

echo "Generated: $OUT_DIR/omle_pb2.py"
