from enum import Enum


class PostApiFollowedPodcastsBodyDataType(str, Enum):
    FOLLOWED_PODCASTS = "followed_podcasts"

    def __str__(self) -> str:
        return str(self.value)
