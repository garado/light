from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Track(_message.Message):
    __slots__ = ("audio_id", "title", "artist", "album", "filename")
    AUDIO_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    ARTIST_FIELD_NUMBER: _ClassVar[int]
    ALBUM_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    audio_id: str
    title: str
    artist: str
    album: str
    filename: str
    def __init__(self, audio_id: _Optional[str] = ..., title: _Optional[str] = ..., artist: _Optional[str] = ..., album: _Optional[str] = ..., filename: _Optional[str] = ...) -> None: ...

class ListTracksRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListTracksResponse(_message.Message):
    __slots__ = ("tracks",)
    TRACKS_FIELD_NUMBER: _ClassVar[int]
    tracks: _containers.RepeatedCompositeFieldContainer[Track]
    def __init__(self, tracks: _Optional[_Iterable[_Union[Track, _Mapping]]] = ...) -> None: ...
