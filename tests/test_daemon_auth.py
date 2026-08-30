"""Auth interceptor: a token-guarded server rejects calls without the token."""

import grpc
import pytest

from light_daemon.auth import bearer_metadata, generate_token, handshake_line
from light_daemon.server import build_server
from light_daemon.testing import FakeLight, FakePw
from light_daemon.v1 import music_pb2, music_pb2_grpc

_TOKEN = "test-token-123"


@pytest.fixture
def channel():
    server, port = build_server(FakePw(FakeLight()), token=_TOKEN)
    server.start()
    chan = grpc.insecure_channel(f"127.0.0.1:{port}")
    try:
        yield chan
    finally:
        chan.close()
        server.stop(grace=None)


def _call(channel, metadata=None):
    stub = music_pb2_grpc.MusicServiceStub(channel)
    return stub.ListTracks(music_pb2.ListTracksRequest(), metadata=metadata)


def test_missing_token_is_unauthenticated(channel):
    with pytest.raises(grpc.RpcError) as exc:
        _call(channel)
    assert exc.value.code() == grpc.StatusCode.UNAUTHENTICATED


def test_wrong_token_is_unauthenticated(channel):
    with pytest.raises(grpc.RpcError) as exc:
        _call(channel, bearer_metadata("not-the-token"))
    assert exc.value.code() == grpc.StatusCode.UNAUTHENTICATED


def test_correct_token_passes(channel):
    resp = _call(channel, bearer_metadata(_TOKEN))
    assert [t.title for t in resp.tracks] == [
        "Playing God",
        "Ego Death",
        "Blackwater Park",
    ]


def test_build_server_requires_a_token():
    with pytest.raises(TypeError):
        build_server(FakePw(FakeLight()))


def test_token_helpers():
    tok = generate_token()
    assert len(tok) >= 32
    assert bearer_metadata(tok) == [("authorization", f"bearer {tok}")]

    import json

    line = json.loads(handshake_line("127.0.0.1", 44227, tok))
    assert line == {"host": "127.0.0.1", "port": 44227, "token": tok}
