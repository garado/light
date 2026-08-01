"""Derive JSON Schema from the dataclasses used with --json."""

import dataclasses
import types
import typing
from typing import Any

_PRIMITIVE_SCHEMAS: dict[type, dict[str, Any]] = {
    str: {"type": "string"},
    int: {"type": "integer"},
    float: {"type": "number"},
    bool: {"type": "boolean"},
}


def dataclass_json_schema(cls: type) -> dict[str, Any]:
    """Build a JSON Schema object for a dataclass's fields."""
    hints = typing.get_type_hints(cls)
    properties: dict[str, Any] = {}
    required: list[str] = []

    for f in dataclasses.fields(cls):
        schema = _type_to_schema(hints[f.name])
        properties[f.name] = schema
        if not schema.get("nullable"):
            required.append(f.name)

    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def _type_to_schema(tp: Any) -> dict[str, Any]:
    """Recursively converts a single Type annotation into its JSON Schema fragment."""

    if tp in _PRIMITIVE_SCHEMAS:
        return dict(_PRIMITIVE_SCHEMAS[tp])

    origin = typing.get_origin(tp)
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
            schema["nullable"] = True
        return schema

    raise NotImplementedError(f"Unsupported type for schema generation: {tp!r}")
