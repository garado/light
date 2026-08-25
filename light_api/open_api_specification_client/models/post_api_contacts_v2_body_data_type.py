from enum import Enum


class PostApiContactsV2BodyDataType(str, Enum):
    CONTACTS = "contacts"

    def __str__(self) -> str:
        return str(self.value)
