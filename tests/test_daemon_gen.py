"""Smoke tests for the generated light_daemon protobuf/gRPC modules."""

import grpc

from light_daemon.v1 import music_pb2, music_pb2_grpc


def test_track_message_roundtrips():
    track = music_pb2.Track(audio_id="abc", title="Playing God", artist="Polyphia")
    restored = music_pb2.Track.FromString(track.SerializeToString())
    assert restored.audio_id == "abc"
    assert restored.title == "Playing God"
    assert restored.artist == "Polyphia"
    # an unset scalar is indistinguishable from its zero value
    assert restored.album == ""
    assert restored.filename == ""


def test_repeated_tracks_behaves_like_a_list():
    resp = music_pb2.ListTracksResponse()
    resp.tracks.add(title="a")
    resp.tracks.add(title="b")
    assert [t.title for t in resp.tracks] == ["a", "b"]
    assert len(resp.tracks) == 2

    restored = music_pb2.ListTracksResponse.FromString(resp.SerializeToString())
    assert [t.title for t in restored.tracks] == ["a", "b"]


def test_service_surface():
    # servicer: ListTracks is a plain (class) method to override
    assert callable(music_pb2_grpc.MusicServiceServicer.ListTracks)
    # registration helper the server bootstrap will use
    assert hasattr(music_pb2_grpc, "add_MusicServiceServicer_to_server")
    # stub: the RPC callable is bound in __init__ from the channel
    with grpc.insecure_channel("localhost:1") as channel:
        stub = music_pb2_grpc.MusicServiceStub(channel)
        assert callable(stub.ListTracks)
