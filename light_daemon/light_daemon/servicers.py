"""gRPC servicer implementations.

All handlers share the same shape: pull fields off `request`, hand the real work to
`self._pw.submit(...)`, map the result back to proto messages.
"""

from __future__ import annotations

from typing import Any

from light_daemon.errors import grpc_errors
from light_daemon.mapping import track_to_proto
from light_daemon.v1 import music_pb2, music_pb2_grpc


class MusicServicer(music_pb2_grpc.MusicServiceServicer):
    def __init__(self, pw: Any) -> None:
        self._pw = pw

    def ListTracks(
        self, request: music_pb2.ListTracksRequest, context: Any
    ) -> music_pb2.ListTracksResponse:
        with grpc_errors(context):
            tracks = self._pw.submit(lambda light: light.music.get_tracks())
            return music_pb2.ListTracksResponse(
                tracks=[track_to_proto(t) for t in tracks]
            )
