#!/usr/bin/env bash
# Regenerate the Python protobuf / gRPC modules from proto/.
#
# Output lands in light_daemon/v1/ (e.g. light_daemon/v1/music_pb2.py).
#
# Run from the light_daemon/ directory:  ./scripts/generate.sh

set -euo pipefail

cd "$(dirname "$0")/.."

python -m grpc_tools.protoc \
  -I proto \
  --python_out=. \
  --grpc_python_out=. \
  --pyi_out=. \
  proto/light_daemon/v1/*.proto

echo "generated:"
ls -1 light_daemon/v1/*_pb2*.py* 2>/dev/null || true
