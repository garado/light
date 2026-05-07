from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_api_playlist_items_response_200 import GetApiPlaylistItemsResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    playlist_ids: str | Unset = UNSET,
    device_tool_id: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["playlist_ids"] = playlist_ids

    params["device_tool_id"] = device_tool_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/playlist_items",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetApiPlaylistItemsResponse200 | None:
    if response.status_code == 200:
        response_200 = GetApiPlaylistItemsResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetApiPlaylistItemsResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    playlist_ids: str | Unset = UNSET,
    device_tool_id: str | Unset = UNSET,
) -> Response[GetApiPlaylistItemsResponse200]:
    """List playlist items

     **Host**: http://production.lightphonecloud.com

    Args:
        playlist_ids (str | Unset):
        device_tool_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiPlaylistItemsResponse200]
    """

    kwargs = _get_kwargs(
        playlist_ids=playlist_ids,
        device_tool_id=device_tool_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    playlist_ids: str | Unset = UNSET,
    device_tool_id: str | Unset = UNSET,
) -> GetApiPlaylistItemsResponse200 | None:
    """List playlist items

     **Host**: http://production.lightphonecloud.com

    Args:
        playlist_ids (str | Unset):
        device_tool_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiPlaylistItemsResponse200
    """

    return sync_detailed(
        client=client,
        playlist_ids=playlist_ids,
        device_tool_id=device_tool_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    playlist_ids: str | Unset = UNSET,
    device_tool_id: str | Unset = UNSET,
) -> Response[GetApiPlaylistItemsResponse200]:
    """List playlist items

     **Host**: http://production.lightphonecloud.com

    Args:
        playlist_ids (str | Unset):
        device_tool_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiPlaylistItemsResponse200]
    """

    kwargs = _get_kwargs(
        playlist_ids=playlist_ids,
        device_tool_id=device_tool_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    playlist_ids: str | Unset = UNSET,
    device_tool_id: str | Unset = UNSET,
) -> GetApiPlaylistItemsResponse200 | None:
    """List playlist items

     **Host**: http://production.lightphonecloud.com

    Args:
        playlist_ids (str | Unset):
        device_tool_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiPlaylistItemsResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            playlist_ids=playlist_ids,
            device_tool_id=device_tool_id,
        )
    ).parsed
