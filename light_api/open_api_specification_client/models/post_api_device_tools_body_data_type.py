from enum import Enum


class PostApiDeviceToolsBodyDataType(str, Enum):
    DEVICE_TOOLS = "device_tools"

    def __str__(self) -> str:
        return str(self.value)
