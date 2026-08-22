"""Derive JSON Schema from the dataclasses used with --json."""

import dataclasses
import hashlib
import json
import types
import typing
from typing import Any

from light_api.devices import LightDevice
from light_api.music import LightTrack, UploadResult
from light_api.notes import LightNote, NoteContentResult, NoteDownloadResult
from light_api.podcast import LightPodcast, PodcastAddResult
from light_api.tools import LightTool

# Map each `--json`-enabled command to its output dataclass.
# NOTE: This isn't autoderived. Must be manually kept in sync w/ any added `render(...)` commands in cli.py.
COMMAND_OUTPUT_SHAPES: dict[str, Any] = {
    "podcasts add": list[PodcastAddResult],
    "podcasts list": list[LightPodcast],
    "podcasts delete": list[LightPodcast],
    "music list": list[LightTrack],
    "music upload": list[UploadResult],
    "notes list": list[LightNote],
    "notes get": NoteContentResult,
    "notes add": LightNote,
    "notes rename": LightNote,
    "notes update": LightNote,
    "notes delete": list[LightNote],
    "notes download-all": list[NoteDownloadResult],
    "tools list": list[LightTool],
    "devices list": list[LightDevice],
}

_PRIMITIVE_SCHEMAS: dict[type, dict[str, Any]] = {
    str: {"type": "string"},
    int: {"type": "integer"},
    float: {"type": "number"},
    bool: {"type": "boolean"},
}


def generate_schema() -> dict[str, Any]:
    """Build full JSON Schema document."""
    return {"$hash": schema_hash(), **_command_schemas()}


def schema_hash() -> str:
    """Get SHA-256 of the canonicalized schema."""
    canonical = json.dumps(_command_schemas(), sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()


def _command_schemas() -> dict[str, Any]:
    return {
        command: {
            "type": "object",
            "properties": {
                "data": _type_to_schema(shape),
                "error": {"anyOf": [{"type": "string"}, {"type": "null"}]},
            },
            "required": ["data", "error"],
            "additionalProperties": False,
        }
        for command, shape in COMMAND_OUTPUT_SHAPES.items()
    }


def _type_to_schema(tp: object) -> dict[str, Any]:
    """Recursively converts a single Type annotation into its JSON Schema fragment."""

    if tp in _PRIMITIVE_SCHEMAS:
        return dict(_PRIMITIVE_SCHEMAS[tp])

    if isinstance(tp, type) and dataclasses.is_dataclass(tp):
        return _dataclass_json_schema(tp)

    origin = typing.get_origin(tp)

    if origin is list:
        (item_type,) = typing.get_args(tp)
        return {"type": "array", "items": _type_to_schema(item_type)}

    if origin is types.UnionType or origin is typing.Union:
        args = typing.get_args(tp)
        nullable = type(None) in args
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) != 1:
            raise NotImplementedError(
                f"Unsupported union for schema generation: {tp!r}"
            )
        schema = _type_to_schema(non_none[0])
        if nullable:
            return {"anyOf": [schema, {"type": "null"}]}
        return schema

    raise NotImplementedError(f"Unsupported type for schema generation: {tp!r}")


def _dataclass_json_schema(cls: type) -> dict[str, Any]:
    """Build a JSON Schema object for a dataclass's fields."""
    hints = typing.get_type_hints(cls)
    fields = dataclasses.fields(cls)

    return {
        "type": "object",
        "properties": {f.name: _type_to_schema(hints[f.name]) for f in fields},
        "required": [f.name for f in fields],
        "additionalProperties": False,
    }
