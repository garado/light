"""Server reflection is off by default, on with `enable_reflection`, and always token-gated."""

import grpc
import pytest
from grpc_reflection.v1alpha import reflection_pb2, reflection_pb2_grpc

from light_daemon.auth import bearer_metadata
from light_daemon.server import build_server
from light_daemon.testing import FakeLight, FakePw

_TOKEN = "reflect-test-token"
_MD = bearer_metadata(_TOKEN)


def _list_services(channel, metadata):
    stub = reflection_pb2_grpc.ServerReflectionStub(channel)
    req = reflection_pb2.ServerReflectionRequest(list_services="")
    resp = next(stub.ServerReflectionInfo(iter([req]), metadata=metadata))
    return {s.name for s in resp.list_services_response.service}


def _server(*, enable_reflection):
    return build_server(
        FakePw(FakeLight()), token=_TOKEN, enable_reflection=enable_reflection
    )


def test_reflection_off_by_default():
    server, port = _server(enable_reflection=False)
    server.start()
    try:
        with grpc.insecure_channel(f"127.0.0.1:{port}") as chan:
            with pytest.raises(grpc.RpcError) as exc:
                _list_services(chan, _MD)
            assert exc.value.code() == grpc.StatusCode.UNIMPLEMENTED
    finally:
        server.stop(grace=None)


def test_reflection_lists_the_service_when_enabled():
    server, port = _server(enable_reflection=True)
    server.start()
    try:
        with grpc.insecure_channel(f"127.0.0.1:{port}") as chan:
            names = _list_services(chan, _MD)
        assert "light_daemon.v1.MusicService" in names
    finally:
        server.stop(grace=None)


def test_reflection_still_needs_the_token():
    server, port = _server(enable_reflection=True)
    server.start()
    try:
        with grpc.insecure_channel(f"127.0.0.1:{port}") as chan:
            with pytest.raises(grpc.RpcError) as exc:
                _list_services(chan, metadata=None)
            assert exc.value.code() == grpc.StatusCode.UNAUTHENTICATED
    finally:
        server.stop(grace=None)
