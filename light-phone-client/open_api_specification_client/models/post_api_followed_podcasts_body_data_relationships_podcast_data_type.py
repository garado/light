from enum import Enum


class PostApiFollowedPodcastsBodyDataRelationshipsPodcastDataType(str, Enum):
    PODCASTS = "podcasts"

    def __str__(self) -> str:
        return str(self.value)
