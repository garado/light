from enum import Enum


class PostApiPlaylistsSortModeBodySortMode(str, Enum):
    ARTISTS_ASC = "artists_asc"
    ARTISTS_DESC = "artists_desc"
    RANK = "rank"

    def __str__(self) -> str:
        return str(self.value)
