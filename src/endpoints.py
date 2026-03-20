"""API endpoint constants for the Light Phone API."""

DASHBOARD = "https://dashboard.thelightphone.com"
API = "https://production.lightphonecloud.com/api"

# Music
PLAYLISTS = f"{API}/playlists"
PLAYLISTS_SORT_MODE = f"{API}/playlists/sort_mode"
PLAYLIST_ITEMS = f"{API}/playlist_items"
AUDIOS = f"{API}/audios"

def audio(audio_id: str) -> str:
    return f"{AUDIOS}/{audio_id}"

def playlist_item(playlist_item_id: str) -> str:
    return f"{PLAYLIST_ITEMS}/{playlist_item_id}"

# Notes
NOTES = f"{API}/notes"

def note(note_id: str) -> str:
    return f"{NOTES}/{note_id}"

def note_presigned_get_url(note_id: str) -> str:
    return f"{NOTES}/{note_id}/generate_presigned_get_url"

# Podcasts
FOLLOWED_PODCASTS = f"{API}/followed_podcasts"
PODCASTS = f"{API}/podcasts"

def followed_podcast(followed_podcast_id: str) -> str:
    return f"{FOLLOWED_PODCASTS}/{followed_podcast_id}"
