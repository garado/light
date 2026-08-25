from enum import Enum


class PostApiContactsV2BodyDataRelationshipsDeviceDataType(str, Enum):
    DEVICES = "devices"

    def __str__(self) -> str:
        return str(self.value)
