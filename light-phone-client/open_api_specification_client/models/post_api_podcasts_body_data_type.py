from enum import Enum


class PostApiPodcastsBodyDataType(str, Enum):
    PODCASTS = "podcasts"

    def __str__(self) -> str:
        return str(self.value)
