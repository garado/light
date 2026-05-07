"""Capture live API responses and save as test fixtures.

Run once with a real device to populate tests/fixtures/.
Requires credentials via env vars or keyring (same as the CLI).

Usage:
    python scripts/capture_fixtures.py
"""

import json
import os
from pathlib import Path

from open_api_specification_client.api.default import (
    get_api_devices,
    get_api_notes,
    get_api_playlists,
    get_api_tools,
)
from light_api.client import Light

FIXTURES = Path(__file__).parent.parent / "tests" / "fixtures"


def capture(name: str, resp) -> None:
    FIXTURES.mkdir(parents=True, exist_ok=True)
    path = FIXTURES / f"{name}.json"
    path.write_text(json.dumps(resp.parsed.to_dict() if hasattr(resp.parsed, "to_dict") else json.loads(resp.content), indent=2))
    print(f"  saved {path} ({resp.status_code})")


def main() -> None:
    with Light(
        email=os.environ.get("LIGHT_EMAIL"),
        email_file=os.environ.get("LIGHT_EMAIL_FILE"),
        password=os.environ.get("LIGHT_PASSWORD"),
        password_file=os.environ.get("LIGHT_PASSWORD_FILE"),
        phone=os.environ.get("LIGHT_PHONE_NUMBER"),
        phone_file=os.environ.get("LIGHT_PHONE_NUMBER_FILE"),
    ) as light:
        client = light._api_client

        print("capturing /api/devices ...")
        resp = light.call_api(get_api_devices.sync_detailed, client=client)
        (FIXTURES / "devices.json").write_text(json.dumps(json.loads(resp.content), indent=2))
        print(f"  saved devices.json ({resp.status_code})")

        device_id = json.loads(resp.content)["data"][0]["id"]

        print("capturing /api/tools ...")
        resp = get_api_tools.sync_detailed(client=client, device_id=device_id)
        (FIXTURES / "tools.json").write_text(json.dumps(json.loads(resp.content), indent=2))
        print(f"  saved tools.json ({resp.status_code})")

        print("capturing /api/notes ...")
        resp = light.call_api(
            get_api_notes.sync_detailed,
            client=client,
            device_tool_id=light._device_tool_ids["notes"],
        )
        (FIXTURES / "notes.json").write_text(json.dumps(json.loads(resp.content), indent=2))
        print(f"  saved notes.json ({resp.status_code})")

        print("capturing /api/playlists ...")
        resp = light.call_api(get_api_playlists.sync_detailed, client=client)
        (FIXTURES / "playlists.json").write_text(json.dumps(json.loads(resp.content), indent=2))
        print(f"  saved playlists.json ({resp.status_code})")

        playlist_id = light._playlist_id
        print("capturing /api/playlist_items ...")
        from open_api_specification_client.api.default import get_api_playlist_items
        resp = light.call_api(
            get_api_playlist_items.sync_detailed,
            client=client,
            playlist_ids=playlist_id,
            device_tool_id=light._device_tool_ids["music"],
        )
        (FIXTURES / "playlist_items.json").write_text(json.dumps(json.loads(resp.content), indent=2))
        print(f"  saved playlist_items.json ({resp.status_code})")


    print("\ndone. commit tests/fixtures/ to lock the contract.")


if __name__ == "__main__":
    main()
