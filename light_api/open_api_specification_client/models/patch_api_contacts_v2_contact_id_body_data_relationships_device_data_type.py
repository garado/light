from enum import Enum


class PatchApiContactsV2ContactIdBodyDataRelationshipsDeviceDataType(str, Enum):
    DEVICES = "devices"

    def __str__(self) -> str:
        return str(self.value)
