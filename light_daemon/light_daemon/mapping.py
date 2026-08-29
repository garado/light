"""Converters between `light_api` dataclasses and generated proto messages."""

from __future__ import annotations

from light_api.music import LightTrack

from light_daemon.v1 import music_pb2


def track_to_proto(track: LightTrack) -> music_pb2.Track:
    return music_pb2.Track(
        audio_id=track.audio_id,
        title=track.title,
        artist=track.artist,
        album=track.album,
        filename=track.filename,
    )
