from enum import Enum


class PatchApiContactsV2ContactIdBodyDataType(str, Enum):
    CONTACTS = "contacts"

    def __str__(self) -> str:
        return str(self.value)
