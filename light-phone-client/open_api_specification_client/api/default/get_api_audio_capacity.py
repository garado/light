from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_api_audio_capacity_response_200 import GetApiAudioCapacityResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    device_tool_id: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["device_tool_id"] = device_tool_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/audio_capacity",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetApiAudioCapacityResponse200 | None:
    if response.status_code == 200:
        response_200 = GetApiAudioCapacityResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetApiAudioCapacityResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    device_tool_id: str | Unset = UNSET,
) -> Response[GetApiAudioCapacityResponse200]:
    """/api/audio_capacity

     **Host**: http://production.lightphonecloud.com

    Args:
        device_tool_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiAudioCapacityResponse200]
    """

    kwargs = _get_kwargs(
        device_tool_id=device_tool_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    device_tool_id: str | Unset = UNSET,
) -> GetApiAudioCapacityResponse200 | None:
    """/api/audio_capacity

     **Host**: http://production.lightphonecloud.com

    Args:
        device_tool_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiAudioCapacityResponse200
    """

    return sync_detailed(
        client=client,
        device_tool_id=device_tool_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    device_tool_id: str | Unset = UNSET,
) -> Response[GetApiAudioCapacityResponse200]:
    """/api/audio_capacity

     **Host**: http://production.lightphonecloud.com

    Args:
        device_tool_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiAudioCapacityResponse200]
    """

    kwargs = _get_kwargs(
        device_tool_id=device_tool_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    device_tool_id: str | Unset = UNSET,
) -> GetApiAudioCapacityResponse200 | None:
    """/api/audio_capacity

     **Host**: http://production.lightphonecloud.com

    Args:
        device_tool_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiAudioCapacityResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            device_tool_id=device_tool_id,
        )
    ).parsed
