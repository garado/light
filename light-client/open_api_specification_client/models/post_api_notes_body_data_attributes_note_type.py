from enum import Enum


class PostApiNotesBodyDataAttributesNoteType(str, Enum):
    AUDIO = "audio"
    TEXT = "text"

    def __str__(self) -> str:
        return str(self.value)
