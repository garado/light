from enum import Enum


class PostApiAudiosBodyDataType(str, Enum):
    AUDIOS = "audios"

    def __str__(self) -> str:
        return str(self.value)
