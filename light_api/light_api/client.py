from __future__ import annotations

import httpx
import json
import keyring
import logging
import os

from typing import TYPE_CHECKING, Any, Callable, Container, Iterable, Iterator, NewType, final

from open_api_specification_client.api.default import get_api_playlists
from open_api_specification_client.client import AuthenticatedClient
from open_api_specification_client.types import Unset

if TYPE_CHECKING:
    from light_api.devices import LightDevices
    from light_api.music import LightMusic
    from light_api.podcast import LightPodcasts
    from light_api.notes import LightNotes
    from light_api.tools import LightTools
    from open_api_specification_client.models.get_api_devices_response_200 import (
        GetApiDevicesResponse200,
    )
    from open_api_specification_client.models.get_api_devices_response_200_included_item import (
        GetApiDevicesResponse200IncludedItem,
    )

KEYRING_SERVICE = "unofficial-light-api"
KEYRING_USER = "session"
API_BASE = "https://production.lightphonecloud.com"
API_HEADERS = {"Accept": "application/vnd.api+json"}

DeviceId = NewType("DeviceId", str)
PhoneNumber = NewType("PhoneNumber", str)

log = logging.getLogger(f"light.{__name__}")


@final
class Light:
    """Methods for interfacing with Light devices."""

    def __init__(
        self,
        email: str | None = None,
        email_file: str | None = None,
        password: str | None = None,
        password_file: str | None = None,
        phone: str | None = None,
        phone_file: str | None = None,
        device_id: str | None = None,
        device_id_file: str | None = None,
    ) -> None:
        self.email: str | None = email or self._resolve(email_file, "LIGHT_EMAIL")
        self.password: str | None = password or self._resolve(
            password_file, "LIGHT_PASSWORD"
        )
        self.phone: str | None = phone or self._resolve(
            phone_file, "LIGHT_PHONE_NUMBER"
        )
        self.device_id: str | None = device_id or self._resolve(
            device_id_file, "LIGHT_DEVICE_ID"
        )

        if self.phone and self.device_id:
            raise RuntimeError(
                "phone and device id are mutually exclusive - provide only one"
            )

        self._api_token: str | None = None
        self._api_client: AuthenticatedClient | None = None
        self._device_tool_ids: dict[str, str] = {}
        self._playlist_id: str | None = None

        self.music: LightMusic
        self.podcast: LightPodcasts
        self.notes: LightNotes
        self.tools: LightTools
        self.devices: LightDevices

    def login(self) -> None:
        """Authenticate via the authorizations API and store the bearer token."""
        if self._api_token is not None:
            return

        if not self.email or not self.password:
            raise RuntimeError("No cached session - provide email and password")

        resp = httpx.post(
            f"{API_BASE}/api/authorizations",
            json={"email": self.email, "password": self.password},
            headers={**API_HEADERS, "Content-Type": "application/vnd.api+json"},
            timeout=30,
        )

        if not resp.is_success:
            raise RuntimeError(f"Login failed: {resp.status_code}")

        included = resp.json()["included"][0]
        token = included["attributes"]["token"]

        if token is None:
            raise RuntimeError("Login succeeded but no token found in response")

        self._api_token = token

    def reauth(self) -> None:
        """Re-authenticate and refresh the API client. Called on 401."""
        log.info("Re-authenticating")
        self._api_token = None
        self.login()
        self._save_cache()
        self._api_client = AuthenticatedClient(
            base_url=API_BASE,
            token=self._api_token,
            headers=API_HEADERS,
        )

    def call_api(self, func: Callable[..., Any], **kwargs: Any) -> Any:
        """Call an API function, re-authenticating once on 401."""
        resp = func(**kwargs)
        if resp.status_code == 401:
            self.reauth()
            resp = func(**kwargs)
        return resp

    @staticmethod
    def _ensure_ok(
        resp: Any,
        action: str,
        ok_codes: Container[int] = (200,),
        require_data: bool = False,
    ) -> Any:
        """Raise RuntimeError(f"{action}: {status}") unless resp is ok, else return resp.parsed.

        Args:
            resp: The API response to parse
            action: Description of the API request being validated. Used in error message.
            ok_codes: Status codes that the caller considers a success
            require_data: True if a non-empty `resp.parsed.data` is required for success

        Returns:
            The parsed data
        """
        if resp.status_code not in ok_codes or (
            require_data and not (resp.parsed and resp.parsed.data)
        ):
            raise RuntimeError(f"{action}: {resp.status_code}")
        return resp.parsed

    def __enter__(self) -> Light:
        """Sets up API session."""
        log.info("Authenticating")

        if self._load_cache() and self._validate_cache():
            log.info("Using cached session")
        else:
            self.login()
            self._save_cache()

        self._api_client = AuthenticatedClient(
            base_url=API_BASE,
            token=self._api_token,
            headers=API_HEADERS,
        )

        expected = {"music", "notes", "podcast"}
        if not expected.issubset(self._device_tool_ids) or not self._playlist_id:
            self._fetch_device_tool_ids()
            self._fetch_playlist_id()
            self._save_cache()

        from light_api.devices import LightDevices
        from light_api.music import LightMusic
        from light_api.podcast import LightPodcasts
        from light_api.notes import LightNotes
        from light_api.tools import LightTools

        self.music = LightMusic(self)
        self.podcast = LightPodcasts(self)
        self.notes = LightNotes(self)
        self.tools = LightTools(self)
        self.devices = LightDevices(self)

        log.info("Authentication complete")
        return self

    def __exit__(self, *_: object) -> None:
        pass

    def _load_cache(self) -> bool:
        """Load cached data from keyring."""
        log.debug("Loading cache")

        try:
            raw = keyring.get_password(KEYRING_SERVICE, KEYRING_USER)
        except (keyring.errors.NoKeyringError, keyring.errors.KeyringLocked) as e:
            log.debug(f"Keyring error: {e}")
            return False

        if raw is None:
            log.debug("Keyring: no entry found")
            return False

        try:
            data = json.loads(raw)
            self._api_token = data["api_token"]
            self._device_tool_ids = data["device_tool_ids"]
            self._playlist_id = data["playlist_id"]
            log.debug("Cache loaded successfully")
            return True
        except (KeyError, json.JSONDecodeError) as e:
            log.debug(f"Error: {e}")
            return False

    def _save_cache(self) -> None:
        """Cache data to keyring."""
        try:
            keyring.set_password(
                KEYRING_SERVICE,
                KEYRING_USER,
                json.dumps(
                    {
                        "api_token": self._api_token,
                        "device_tool_ids": self._device_tool_ids,
                        "playlist_id": self._playlist_id,
                    }
                ),
            )
        except (keyring.errors.NoKeyringError, keyring.errors.KeyringLocked) as e:
            log.warning(f"Keyring error: {e}")

    def _validate_cache(self) -> bool:
        """Check if cached auth token is valid."""
        client = AuthenticatedClient(
            base_url=API_BASE,
            token=self._api_token,
            headers=API_HEADERS,
        )
        resp = get_api_playlists.sync_detailed(
            client=client,
            device_tool_id=self._device_tool_ids.get("music"),
        )
        return resp.status_code == 200

    def _fetch_playlist_id(self) -> None:
        music_id = self._device_tool_ids.get("music")
        if not music_id:
            raise RuntimeError("Could not find music device_tool_id in /api/devices")
        resp = get_api_playlists.sync_detailed(
            client=self._api_client,
            device_tool_id=music_id,
        )
        parsed = self._ensure_ok(resp, "Could not fetch playlists", require_data=True)
        self._playlist_id = parsed.data[0].id

    def _fetch_device_tool_ids(self) -> None:
        """Populate _device_tool_ids for all installed tools.

        The Light API has two relevant endpoints:
          - GET /api/devices: returns the device record plus "included" items which are
            device_tool records (one per installed tool). Each has a unique `id` (the
            device_tool_id used in subsequent API calls) and a relationship pointing to
            its global tool ID.
          - GET /api/tools?device_id=...: returns the global tool catalog with human-readable
            namespace strings (e.g. "com.light.music", "com.light.notes").

        To get each device tool id, cross-reference the two: build a map of global_tool_id -> namespace
        from /api/tools, then walk the /api/devices included items, look up each item's global tool ID in
        that map, and classify it as "music", "notes", or "podcast" based on the namespace string.
        """
        from open_api_specification_client.api.default import (
            get_api_devices,
            get_api_tools,
        )

        devices_resp = get_api_devices.sync_detailed(client=self._api_client)
        devices = self._ensure_ok(devices_resp, "Could not fetch devices", require_data=True)
        device_id = self._select_device_id(devices)

        tools_resp = get_api_tools.sync_detailed(
            client=self._api_client, device_id=device_id
        )
        tools = self._ensure_ok(tools_resp, "Could not fetch tools")

        tool_ns: dict[str, str] = {
            t.id: t.attributes.namespace.lower() for t in tools.data
        }

        for item in self._device_tool_items(devices.included, device_id):
            ns = tool_ns.get(item.relationships.tool.data.id, "")
            if "note" in ns:
                self._device_tool_ids["notes"] = item.id
            elif "podcast" in ns:
                self._device_tool_ids["podcast"] = item.id
            elif "music" in ns or "playlist" in ns:
                self._device_tool_ids["music"] = item.id

    @staticmethod
    def _device_tool_items(
        included: Iterable[GetApiDevicesResponse200IncludedItem], device_id: DeviceId
    ) -> Iterator[GetApiDevicesResponse200IncludedItem]:
        """Yield the device_tool items in `included` belonging to `device_id`."""
        for item in included:
            if isinstance(item.relationships, Unset) or isinstance(
                item.relationships.tool, Unset
            ):
                continue
            if item.relationships.device.data.id != device_id:
                continue
            yield item

    @staticmethod
    def _device_phone_numbers(
        included: Iterable[GetApiDevicesResponse200IncludedItem],
    ) -> Iterator[tuple[DeviceId, PhoneNumber]]:
        """Yield (device_id, phone_number) pairs from the sims records in `included`."""
        for item in included:
            if item.type_ != "sims" or isinstance(item.attributes.phone_number, Unset):
                continue
            yield DeviceId(item.relationships.device.data.id), PhoneNumber(
                item.attributes.phone_number
            )

    def _select_device_id(self, devices: GetApiDevicesResponse200) -> DeviceId:
        """Select the correct device id out of /api/devices data.

        Matches on this criteria, in order:
        - self.device_id
        - self.phone
        - a single device, if only one device is present

        Raises if none of the above resolves to a single device.
        """
        data = devices.data

        if self.device_id:
            for d in data:
                if d.id == self.device_id:
                    return DeviceId(d.id)

            available = ", ".join(d.id for d in data)
            raise RuntimeError(
                f"No device found with id {self.device_id!r}. "
                f"Available device ids: {available}"
            )

        if self.phone:
            target = self._phone_digits(self.phone)
            seen: list[str] = []

            for device_id, number in self._device_phone_numbers(devices.included):
                if self._phone_digits(number) == target:
                    return device_id
                seen.append(f"{device_id} ({number})")

            raise RuntimeError(
                f"No device found matching phone number {self.phone!r}. "
                f"Available devices: {', '.join(seen)}"
            )

        if len(data) == 1:
            return DeviceId(data[0].id)

        raise RuntimeError(
            "Multiple devices found on this account - specify one via "
            "--device-id or --phone-number. Available device ids: "
            + ", ".join(d.id for d in data)
        )

    @staticmethod
    def _phone_digits(number: str) -> str:
        """Normalizes phone numbers to a bare 10-digit string.

        TODO: This is America-centric.
        """
        return "".join(c for c in number if c.isdigit())[-10:]

    @staticmethod
    def _format_phone(number: str) -> str:
        digits = Light._phone_digits(number)
        return f"+1 {digits[0:3]} {digits[3:6]} {digits[6:10]}"

    @staticmethod
    def _resolve(filepath: str | None, env_key: str) -> str | None:
        if filepath:
            try:
                with open(filepath) as f:
                    return f.read().strip()
            except OSError as e:
                raise RuntimeError(f"Could not read {filepath}: {e}") from e
        return os.environ.get(env_key)
