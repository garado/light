"""Shared non-fixture helpers for light_api tests."""

from types import SimpleNamespace

from light_api.client import Light

API = "https://production.lightphonecloud.com"


def make_light(phone: str | None = None, device_id: str | None = None) -> Light:
    """Return a Light instance with auth bypassed."""
    from open_api_specification_client.client import AuthenticatedClient
    from light_api.music import LightMusic
    from light_api.notes import LightNotes
    from light_api.tools import LightTools
    from light_api.podcast import LightPodcasts
    light = Light(email="test@example.com", password="test", phone=phone, device_id=device_id)
    light._api_token = "fake-token"
    light._api_client = AuthenticatedClient(base_url=API, token="fake-token")
    light._music = LightMusic(light)
    light._notes = LightNotes(light)
    light._tools = LightTools(light)
    light._podcast = LightPodcasts(light)
    light._playlist_id = "fake-playlist-id"
    return light


def fake_resp(status_code: int, parsed=None):
    return SimpleNamespace(status_code=status_code, parsed=parsed)
