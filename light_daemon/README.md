# light-phone-daemon

A local gRPC daemon that holds an authenticated Light Phone session and exposes
it to other processes, so tools in any language can depend on it.

**Status:** early scaffolding. Not usable - yet!

## Layout

- `proto/` - protobuf contract
- `light_daemon/v1/` - generated protobuf / gRPC modules.
    - Regenerate with `./scripts/generate.sh` after changing anything under `proto/`.
