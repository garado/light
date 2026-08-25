from enum import Enum


class PatchApiDevicesDeviceIdDeveloperModeBodyDataType(str, Enum):
    DEVICE = "device"

    def __str__(self) -> str:
        return str(self.value)
