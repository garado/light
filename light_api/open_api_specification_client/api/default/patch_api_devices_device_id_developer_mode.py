from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.patch_api_devices_device_id_developer_mode_body import PatchApiDevicesDeviceIdDeveloperModeBody
from ...models.patch_api_devices_device_id_developer_mode_response_200 import (
    PatchApiDevicesDeviceIdDeveloperModeResponse200,
)
from ...types import Response


def _get_kwargs(
    device_id: str,
    *,
    body: PatchApiDevicesDeviceIdDeveloperModeBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/api/devices/{device_id}/developer_mode".format(
            device_id=quote(str(device_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/vnd.api+json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PatchApiDevicesDeviceIdDeveloperModeResponse200 | None:
    if response.status_code == 200:
        response_200 = PatchApiDevicesDeviceIdDeveloperModeResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PatchApiDevicesDeviceIdDeveloperModeResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    device_id: str,
    *,
    client: AuthenticatedClient,
    body: PatchApiDevicesDeviceIdDeveloperModeBody,
) -> Response[PatchApiDevicesDeviceIdDeveloperModeResponse200]:
    """Set developer mode on a device

     **Host**: http://production.lightphonecloud.com

    Args:
        device_id (str):
        body (PatchApiDevicesDeviceIdDeveloperModeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PatchApiDevicesDeviceIdDeveloperModeResponse200]
    """

    kwargs = _get_kwargs(
        device_id=device_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    device_id: str,
    *,
    client: AuthenticatedClient,
    body: PatchApiDevicesDeviceIdDeveloperModeBody,
) -> PatchApiDevicesDeviceIdDeveloperModeResponse200 | None:
    """Set developer mode on a device

     **Host**: http://production.lightphonecloud.com

    Args:
        device_id (str):
        body (PatchApiDevicesDeviceIdDeveloperModeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PatchApiDevicesDeviceIdDeveloperModeResponse200
    """

    return sync_detailed(
        device_id=device_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    device_id: str,
    *,
    client: AuthenticatedClient,
    body: PatchApiDevicesDeviceIdDeveloperModeBody,
) -> Response[PatchApiDevicesDeviceIdDeveloperModeResponse200]:
    """Set developer mode on a device

     **Host**: http://production.lightphonecloud.com

    Args:
        device_id (str):
        body (PatchApiDevicesDeviceIdDeveloperModeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PatchApiDevicesDeviceIdDeveloperModeResponse200]
    """

    kwargs = _get_kwargs(
        device_id=device_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    device_id: str,
    *,
    client: AuthenticatedClient,
    body: PatchApiDevicesDeviceIdDeveloperModeBody,
) -> PatchApiDevicesDeviceIdDeveloperModeResponse200 | None:
    """Set developer mode on a device

     **Host**: http://production.lightphonecloud.com

    Args:
        device_id (str):
        body (PatchApiDevicesDeviceIdDeveloperModeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PatchApiDevicesDeviceIdDeveloperModeResponse200
    """

    return (
        await asyncio_detailed(
            device_id=device_id,
            client=client,
            body=body,
        )
    ).parsed
