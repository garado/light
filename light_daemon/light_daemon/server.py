"""Wire servicers onto a loopback-only gRPC server."""

from __future__ import annotations

from concurrent import futures
from typing import Any

import grpc

from light_daemon.servicers import MusicServicer
from light_daemon.v1 import music_pb2_grpc

# One worker since the Light session isn't threadsafe
_MAX_WORKERS = 1


def build_server(pw: Any, port: int = 0) -> tuple[grpc.Server, int]:
    """Build (but do not start) a gRPC server bound to `host:port`.

    Args:
        pw: Proxy worker
        port: Port to assign. '0' allows OS to autoassign it.

    Returns:
        Tuple: [0] grpc server instance, and [1] port.
    """
    host = "127.0.0.1"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=_MAX_WORKERS))

    music_pb2_grpc.add_MusicServiceServicer_to_server(MusicServicer(pw), server)

    bound_port = server.add_insecure_port(f"{host}:{port}")
    return server, bound_port


def serve(pw: Any, port: int = 0) -> None:
    """Build, start, and block on a server until interrupted.

    Args:
        pw: Proxy worker
        port: Port to assign. '0' allows OS to autoassign it.
    """
    host = "127.0.0.1"
    server, bound_port = build_server(pw, port)
    server.start()
    print(f"light-daemon listening on {host}:{bound_port}", flush=True)

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(grace=1)
    finally:
        pw.shutdown()
