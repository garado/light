"""Wire servicers onto a loopback-only gRPC server."""

from __future__ import annotations

import signal
import sys
from concurrent import futures
from typing import Any

import grpc
from grpc_reflection.v1alpha import reflection

from light_daemon.auth import AuthInterceptor, handshake_line
from light_daemon.servicers import MusicServicer
from light_daemon.v1 import music_pb2, music_pb2_grpc

# One worker since the Light session isn't threadsafe
_MAX_WORKERS = 1

# Seconds to let in-flight RPCs finish on shutdown
_SHUTDOWN_GRACE_SECONDS = 5


def build_server(
    pw: Any, *, token: str, port: int = 0, enable_reflection: bool = False
) -> tuple[grpc.Server, int]:
    """Build (but do not start) a gRPC server bound to `host:port`.

    Args:
        pw: Proxy worker
        token: Every RPC must carry this as `bearer` auth metadata.
        port: Port to assign. '0' allows OS to autoassign it.
        enable_reflection: expose gRPC server reflection (still token-gated). Off by default.

    Returns:
        Tuple: [0] grpc server instance, and [1] port.
    """
    host = "127.0.0.1"
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=_MAX_WORKERS),
        interceptors=[AuthInterceptor(token)],
    )

    music_pb2_grpc.add_MusicServiceServicer_to_server(MusicServicer(pw), server)

    if enable_reflection:
        reflection.enable_server_reflection(
            (
                music_pb2.DESCRIPTOR.services_by_name["MusicService"].full_name,
                reflection.SERVICE_NAME,
            ),
            server,
        )

    bound_port = server.add_insecure_port(f"{host}:{port}")
    return server, bound_port


def serve(
    pw: Any, *, token: str, port: int = 0, enable_reflection: bool = False
) -> None:
    """Build, start, and block on a server until interrupted.

    Args:
        pw: Proxy worker
        token: Bearer token required on every RPC.
        port: Port to assign. '0' allows OS to autoassign it.
        enable_reflection: expose gRPC server reflection (see `build_server`).
    """
    host = "127.0.0.1"
    server, bound_port = build_server(
        pw, token=token, port=port, enable_reflection=enable_reflection
    )

    def _shutdown(signum, _frame):
        # non-blocking: schedules a graceful stop, then wait_for_termination() returns
        server.stop(_SHUTDOWN_GRACE_SECONDS)

    signal.signal(signal.SIGINT, _shutdown)  # Ctrl+C
    signal.signal(signal.SIGTERM, _shutdown)  # `kill`, systemd, etc.

    server.start()

    print(handshake_line(host, bound_port, token), flush=True)
    print(f"light-daemon listening on {host}:{bound_port}", file=sys.stderr, flush=True)

    try:
        server.wait_for_termination()
    finally:
        pw.shutdown()
