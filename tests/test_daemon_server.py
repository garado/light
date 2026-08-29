"""End-to-end slice: real gRPC server + real generated stub + fake session.

Proves the wiring - proto -> servicer -> server -> socket -> stub - without
needing Light credentials.
"""

import grpc
import pytest

from light_daemon.server import build_server
from light_daemon.testing import FakeLight, FakePw
from light_daemon.v1 import music_pb2, music_pb2_grpc


@pytest.fixture
def channel():
    server, port = build_server(FakePw(FakeLight()))
    server.start()
    chan = grpc.insecure_channel(f"127.0.0.1:{port}")
    try:
        yield chan
    finally:
        chan.close()
        server.stop(grace=None)


def test_list_tracks_returns_the_fake_library(channel):
    stub = music_pb2_grpc.MusicServiceStub(channel)
    resp = stub.ListTracks(music_pb2.ListTracksRequest())

    assert [t.title for t in resp.tracks] == [
        "Playing God",
        "Ego Death",
        "Blackwater Park",
    ]
    first = resp.tracks[0]
    assert first.audio_id == "aud-1"
    assert first.artist == "Polyphia"
    assert first.album == "Remember That You Will Die"
    assert first.filename == "01 Playing God.mp3"


def test_server_gets_an_os_assigned_port():
    server, port = build_server(FakePw(FakeLight()))
    try:
        assert port != 0
    finally:
        server.stop(grace=None)


def test_unknown_method_is_unimplemented(channel):
    bogus = channel.unary_unary(
        "/light_daemon.v1.MusicService/DoesNotExist",
        request_serializer=music_pb2.ListTracksRequest.SerializeToString,
        response_deserializer=music_pb2.ListTracksResponse.FromString,
    )
    with pytest.raises(grpc.RpcError) as exc:
        bogus(music_pb2.ListTracksRequest())
    assert exc.value.code() == grpc.StatusCode.UNIMPLEMENTED
