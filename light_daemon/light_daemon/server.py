"""Wire servicers onto a loopback-only gRPC server."""

from __future__ import annotations

import signal
import sys
from concurrent import futures
from typing import Any

import grpc

from light_daemon.auth import AuthInterceptor, handshake_line
from light_daemon.servicers import MusicServicer
from light_daemon.v1 import music_pb2_grpc

# One worker since the Light session isn't threadsafe
_MAX_WORKERS = 1

# Seconds to let in-flight RPCs finish on shutdown
_SHUTDOWN_GRACE_SECONDS = 5


def build_server(pw: Any, *, token: str, port: int = 0) -> tuple[grpc.Server, int]:
    """Build (but do not start) a gRPC server bound to `host:port`.

    Args:
        pw: Proxy worker
        token: Every RPC must carry this as `bearer` auth metadata.
        port: Port to assign. '0' allows OS to autoassign it.

    Returns:
        Tuple: [0] grpc server instance, and [1] port.
    """
    host = "127.0.0.1"
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=_MAX_WORKERS),
        interceptors=[AuthInterceptor(token)],
    )

    music_pb2_grpc.add_MusicServiceServicer_to_server(MusicServicer(pw), server)

    bound_port = server.add_insecure_port(f"{host}:{port}")
    return server, bound_port


def serve(pw: Any, *, token: str, port: int = 0) -> None:
    """Build, start, and block on a server until interrupted.

    Args:
        pw: Proxy worker
        token: Bearer token required on every RPC.
        port: Port to assign. '0' allows OS to autoassign it.
    """
    host = "127.0.0.1"
    server, bound_port = build_server(pw, token=token, port=port)
    server.start()
    # one machine-readable line on stdout for a parent process to consume
    print(handshake_line(host, bound_port, token), flush=True)
    print(f"light-daemon listening on {host}:{bound_port}", file=sys.stderr, flush=True)

    def _shutdown(signum, _frame):
        # non-blocking: schedules a graceful stop, then wait_for_termination() returns
        server.stop(_SHUTDOWN_GRACE_SECONDS)

    signal.signal(signal.SIGINT, _shutdown)  # Ctrl+C
    signal.signal(signal.SIGTERM, _shutdown)  # `kill`, systemd, etc.

    try:
        server.wait_for_termination()
    finally:
        pw.shutdown()
