from enum import Enum


class PostApiFollowedPodcastsBodyDataRelationshipsDeviceToolDataType(str, Enum):
    DEVICE_TOOLS = "device_tools"

    def __str__(self) -> str:
        return str(self.value)
