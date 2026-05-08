from enum import Enum


class PatchApiPlaylistItemsPlaylistItemIdBodyDataType(str, Enum):
    PLAYLIST_ITEMS = "playlist_items"

    def __str__(self) -> str:
        return str(self.value)
