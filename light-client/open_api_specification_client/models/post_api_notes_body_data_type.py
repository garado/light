from enum import Enum


class PostApiNotesBodyDataType(str, Enum):
    NOTES = "notes"

    def __str__(self) -> str:
        return str(self.value)
