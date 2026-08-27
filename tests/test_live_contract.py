"""Live contract test - validate real Light API responses against openapi-spec.json.

Requires real credentials and a registered device. Excluded from CI.

Run:

    nix develop
    LIGHT_EMAIL=you@example.com LIGHT_PASSWORD=... \\
        uv run pytest tests/test_live_contract.py --live -v

For a multi-device account also set LIGHT_PHONE_NUMBER or LIGHT_DEVICE_ID.
Pass --strict-extra to also fail when a response carries fields the spec is missing
(i.e. upstream added something).

A failure here means the live API drifted from light_api/openapi-spec.json.
"""

import json
import os
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

pytestmark = pytest.mark.live

SPEC = json.loads(
    (Path(__file__).parent.parent / "light_api" / "openapi-spec.json").read_text()
)


# --------------------------------------------------------------------------- #
# spec -> validator
# --------------------------------------------------------------------------- #
def _openapi_to_jsonschema(node):
    """Normalize the OpenAPI 3.0-style `nullable: true` into JSON Schema 2020-12.

    the spec mixes 3.1 (`anyOf` with `{"type": "null"}`) and a couple of leftover
    3.0 `nullable: true` objects; the latter is an unknown keyword under 2020-12
    and would otherwise make a legitimate `null` fail validation.
    """
    if isinstance(node, list):
        return [_openapi_to_jsonschema(x) for x in node]
    if not isinstance(node, dict):
        return node
    out = {k: _openapi_to_jsonschema(v) for k, v in node.items()}
    if out.pop("nullable", False):
        return {"anyOf": [out, {"type": "null"}]} if out else {"type": "null"}
    return out


def _strict_no_extra(node):
    """Recursively forbid undocumented properties on closed object schemas."""
    if isinstance(node, list):
        return [_strict_no_extra(x) for x in node]
    if not isinstance(node, dict):
        return node
    out = {k: _strict_no_extra(v) for k, v in node.items()}
    if (
        out.get("type") == "object"
        and "properties" in out
        and "additionalProperties" not in out
    ):
        out["additionalProperties"] = False
    return out


def _response_schema(path_template: str, status: int):
    """The JSON response schema the spec documents for GET path_template @ status."""
    responses = SPEC["paths"][path_template]["get"]["responses"]
    assert str(status) in responses, (
        f"GET {path_template} returned undocumented status {status} "
        f"(spec documents {sorted(responses)})"
    )
    content = responses[str(status)].get("content", {})
    for media_type, media in content.items():
        if "json" in media_type:
            return media["schema"]
    return None


def _assert_matches(path_template: str, resp, strict: bool):
    schema = _response_schema(path_template, resp.status_code)
    if schema is None:
        pytest.skip(
            f"spec documents no JSON body for {path_template} {resp.status_code}"
        )
    schema = _openapi_to_jsonschema(schema)
    if strict:
        schema = _strict_no_extra(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(resp.json()),
        key=lambda e: list(e.path),
    )
    if errors:
        report = "\n".join(
            f"  $.{'.'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors
        )
        pytest.fail(
            f"{path_template} response does not match openapi-spec.json:\n{report}",
            pytrace=False,
        )


# --------------------------------------------------------------------------- #
# live session
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="session")
def live():
    from light_api.client import Light

    if not (os.environ.get("LIGHT_EMAIL") or os.environ.get("LIGHT_EMAIL_FILE")):
        pytest.skip(
            "set LIGHT_EMAIL / LIGHT_PASSWORD (+ LIGHT_PHONE_NUMBER or "
            "LIGHT_DEVICE_ID for multi-device accounts)"
        )

    light = Light(
        email=os.environ.get("LIGHT_EMAIL"),
        email_file=os.environ.get("LIGHT_EMAIL_FILE"),
        password=os.environ.get("LIGHT_PASSWORD"),
        password_file=os.environ.get("LIGHT_PASSWORD_FILE"),
        phone=os.environ.get("LIGHT_PHONE_NUMBER"),
        phone_file=os.environ.get("LIGHT_PHONE_NUMBER_FILE"),
        device_id=os.environ.get("LIGHT_DEVICE_ID"),
    )
    with light:
        yield light


def _get(light, path: str, params: dict | None = None):
    """Raw GET through the authenticated client, re-authing once on 401."""

    def once():
        return light._api_client.get_httpx_client().get(path, params=params or {})

    resp = once()
    if resp.status_code == 401:
        light.reauth()
        resp = once()
    return resp


# --------------------------------------------------------------------------- #
# endpoints with static params
# --------------------------------------------------------------------------- #
# (test id, path template, params builder). A param that resolves to None means a
# prerequisite (e.g. an uninstalled tool) is missing and the case is skipped.
ENDPOINTS = [
    ("users_current", "/api/users/current", lambda l: {}),
    ("devices", "/api/devices", lambda l: {}),
    ("tools", "/api/tools", lambda l: {"device_id": l.current_device_id}),
    (
        "audio_capacity",
        "/api/audio_capacity",
        lambda l: {"device_tool_id": l._device_tool_ids.get("music")},
    ),
    (
        "playlists",
        "/api/playlists",
        lambda l: {"device_tool_id": l._device_tool_ids.get("music")},
    ),
    (
        "playlist_items",
        "/api/playlist_items",
        lambda l: {
            "playlist_ids": l._playlist_id,
            "device_tool_id": l._device_tool_ids.get("music"),
        },
    ),
    (
        "followed_podcasts",
        "/api/followed_podcasts",
        lambda l: {"device_tool_id": l._device_tool_ids.get("podcast")},
    ),
    (
        "notes",
        "/api/notes",
        lambda l: {"device_tool_id": l._device_tool_ids.get("notes")},
    ),
    ("contacts_v2", "/api/contacts_v2", lambda l: {"device_id": l.current_device_id}),
    ("podcasts", "/api/podcasts", lambda l: {"title": "npr"}),
]


@pytest.mark.parametrize(
    "path,build_params",
    [(p, b) for _, p, b in ENDPOINTS],
    ids=[i for i, _, _ in ENDPOINTS],
)
def test_response_matches_spec(live, request, path, build_params):
    params = build_params(live)
    missing = [k for k, v in params.items() if v is None]
    if missing:
        pytest.skip(f"missing prerequisite(s): {', '.join(missing)}")
    resp = _get(live, path, params)
    _assert_matches(path, resp, request.config.getoption("--strict-extra"))


# --------------------------------------------------------------------------- #
# endpoints needing an id discovered at runtime
# --------------------------------------------------------------------------- #
def test_note_by_id_matches_spec(live, request):
    dtid = live._device_tool_ids.get("notes")
    if not dtid:
        pytest.skip("notes tool not installed")
    listing = _get(live, "/api/notes", {"device_tool_id": dtid}).json()
    data = listing.get("data") or []
    if not data:
        pytest.skip("account has no notes")
    resp = _get(live, f"/api/notes/{data[0]['id']}", {"device_tool_id": dtid})
    _assert_matches(
        "/api/notes/{note_id}", resp, request.config.getoption("--strict-extra")
    )


def test_tool_by_id_matches_spec(live, request):
    listing = _get(live, "/api/tools", {"device_id": live.current_device_id}).json()
    data = listing.get("data") or []
    if not data:
        pytest.skip("no tools returned")
    resp = _get(live, f"/api/tools/{data[0]['id']}")
    _assert_matches(
        "/api/tools/{tool_id}", resp, request.config.getoption("--strict-extra")
    )
