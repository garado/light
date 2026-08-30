"""Ensure API failures surface as sensible gRPC status codes, not UNKNOWN."""

import grpc
import httpx
import pytest

from light_daemon.auth import bearer_metadata
from light_daemon.server import build_server
from light_daemon.testing import FakeLight, FakePw
from light_daemon.v1 import music_pb2, music_pb2_grpc

_TOKEN = "err-test-token"
_MD = bearer_metadata(_TOKEN)


def _list_tracks_with(raises):
    server, port = build_server(FakePw(FakeLight(raises=raises)), token=_TOKEN)
    server.start()
    try:
        with grpc.insecure_channel(f"127.0.0.1:{port}") as chan:
            stub = music_pb2_grpc.MusicServiceStub(chan)
            with pytest.raises(grpc.RpcError) as exc:
                stub.ListTracks(music_pb2.ListTracksRequest(), metadata=_MD)
            return exc.value
    finally:
        server.stop(grace=None)


@pytest.mark.parametrize(
    "raises, expected",
    [
        (httpx.TimeoutException("slow"), grpc.StatusCode.DEADLINE_EXCEEDED),
        (httpx.ConnectError("refused"), grpc.StatusCode.UNAVAILABLE),
        (
            RuntimeError("No cached session and no credentials available."),
            grpc.StatusCode.UNAUTHENTICATED,
        ),
        (
            RuntimeError("Multiple devices found - specify one via --device-id"),
            grpc.StatusCode.FAILED_PRECONDITION,
        ),
        (ValueError("something odd"), grpc.StatusCode.INTERNAL),
    ],
)
def test_error_mapping(raises, expected):
    err = _list_tracks_with(raises)
    assert err.code() == expected
    assert err.details()  # original message is carried through, not swallowed
