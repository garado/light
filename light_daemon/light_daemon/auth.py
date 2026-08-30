"""Per-instance bearer-token auth for the daemon.

The daemon generates one random token per invocation. Every RPC must carry it as
`authorization: bearer <token>` metadata. A serverside interceptor rejects the rest
with UNAUTHENTICATED. The token reaches the client via a stdout handshake line.
"""

from __future__ import annotations

import json
import secrets

import grpc

_SCHEME = "bearer"
_METADATA_KEY = "authorization"
_DENY_MESSAGE = "missing or invalid token"


def generate_token() -> str:
    """A fresh, high-entropy token for one daemon run."""
    return secrets.token_urlsafe(32)


def bearer_metadata(token: str) -> list[tuple[str, str]]:
    """Call metadata that a client attaches to every RPC: `metadata=bearer_metadata(tok)`."""
    return [(_METADATA_KEY, f"{_SCHEME} {token}")]


def handshake_line(host: str, port: int, token: str) -> str:
    """The single JSON line the daemon prints to stdout on start for a parent process to read."""
    return json.dumps({"host": host, "port": port, "token": token})


def _deny_unary(request, context):
    context.abort(grpc.StatusCode.UNAUTHENTICATED, _DENY_MESSAGE)


def _deny_stream(request, context):
    context.abort(grpc.StatusCode.UNAUTHENTICATED, _DENY_MESSAGE)
    yield  # unreachable (abort raises) - present so this is a generator function


def _deny_handler(handler: grpc.RpcMethodHandler) -> grpc.RpcMethodHandler:
    """A handler of the same cardinality as `handler` that always aborts."""
    if handler.request_streaming and handler.response_streaming:
        return grpc.stream_stream_rpc_method_handler(_deny_stream)
    if handler.request_streaming:
        return grpc.stream_unary_rpc_method_handler(_deny_unary)
    if handler.response_streaming:
        return grpc.unary_stream_rpc_method_handler(_deny_stream)
    return grpc.unary_unary_rpc_method_handler(_deny_unary)


class AuthInterceptor(grpc.ServerInterceptor):
    """Reject any call whose `authorization` metadata isn't `bearer <token>`."""

    def __init__(self, token: str) -> None:
        self._expected = f"{_SCHEME} {token}"

    def intercept_service(self, continuation, handler_call_details):
        handler = continuation(handler_call_details)
        if handler is None:
            return None  # unknown method - let gRPC return UNIMPLEMENTED
        md = dict(handler_call_details.invocation_metadata or ())
        if md.get(_METADATA_KEY) == self._expected:
            return handler
        return _deny_handler(handler)
