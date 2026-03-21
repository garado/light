"""API endpoint constants for the Light Phone API."""

DASHBOARD = "https://dashboard.thelightphone.com"
API = "https://production.lightphonecloud.com/api"

# Music
PLAYLISTS = f"{API}/playlists"
PLAYLISTS_SORT_MODE = f"{API}/playlists/sort_mode"
PLAYLIST_ITEMS = f"{API}/playlist_items"
AUDIOS = f"{API}/audios"

# Notes
NOTES = f"{API}/notes"

# Podcasts
FOLLOWED_PODCASTS = f"{API}/followed_podcasts"
PODCASTS = f"{API}/podcasts"


def audio(audio_id: str) -> str:
    return f"{AUDIOS}/{audio_id}"


def playlist_item(playlist_item_id: str) -> str:
    return f"{PLAYLIST_ITEMS}/{playlist_item_id}"


def playlists(playlist_id: str, device_tool_id: str) -> str:
    return f"{PLAYLISTS}?playlist_ids={playlist_id}&device_tool_id={device_tool_id}"


def playlist_items(playlist_id: str, device_tool_id: str) -> str:
    return (
        f"{PLAYLIST_ITEMS}?playlist_ids={playlist_id}&device_tool_id={device_tool_id}"
    )


def note(note_id: str, device_tool_id: str) -> str:
    return f"{NOTES}/{note_id}?device_tool_id={device_tool_id}"


def note_presigned_get_url(note_id: str) -> str:
    return f"{NOTES}/{note_id}/generate_presigned_get_url"


def notes(device_tool_id: str) -> str:
    return f"{NOTES}?device_tool_id={device_tool_id}"


def followed_podcast(followed_podcast_id: str) -> str:
    return f"{FOLLOWED_PODCASTS}/{followed_podcast_id}"


def followed_podcasts(device_tool_id: str) -> str:
    return f"{FOLLOWED_PODCASTS}?device_tool_id={device_tool_id}"
