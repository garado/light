"""In-memory fakes for developing and testing the daemon without a real session.

`FakePw` matches the `.submit(fn)` shape of `light_api`'s worker thread, so it
drops in wherever the real one goes. `FakeLight` mimics enough of `light_api`'s
`Light` surface for the servicers to call.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from light_api.music import LightTrack

_SAMPLE_TRACKS = [
    LightTrack(
        playlist_item_id="pi-1",
        playlist_id="pl-1",
        audio_id="aud-1",
        title="Playing God",
        artist="Polyphia",
        album="Remember That You Will Die",
        filename="01 Playing God.mp3",
    ),
    LightTrack(
        playlist_item_id="pi-2",
        playlist_id="pl-1",
        audio_id="aud-2",
        title="Ego Death",
        artist="Polyphia",
        album="Remember That You Will Die",
        filename="09 Ego Death.mp3",
    ),
    LightTrack(
        playlist_item_id="pi-3",
        playlist_id="pl-1",
        audio_id="aud-3",
        title="Blackwater Park",
        artist="Opeth",
        album="Blackwater Park",
        filename="blackwater_park.flac",
    ),
]


class _FakeMusic:
    def __init__(self, tracks: list[LightTrack]) -> None:
        self._tracks = tracks

    def get_tracks(self) -> list[LightTrack]:
        return list(self._tracks)


class FakeLight:
    """Stand-in for `light_api.client.Light`."""

    def __init__(self, tracks: list[LightTrack] | None = None) -> None:
        self.music = _FakeMusic(_SAMPLE_TRACKS if tracks is None else tracks)


@dataclass
class FakePw:
    """Stand-in for the background worker: runs the callable inline."""

    light: Any

    def submit(self, func: Callable[[Any], Any]) -> Any:
        return func(self.light)

    def shutdown(self) -> None:  # parity with the real worker
        pass
