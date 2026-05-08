from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.patch_api_playlist_items_playlist_item_id_body import PatchApiPlaylistItemsPlaylistItemIdBody
from ...models.patch_api_playlist_items_playlist_item_id_response_200 import (
    PatchApiPlaylistItemsPlaylistItemIdResponse200,
)
from ...types import Response


def _get_kwargs(
    playlist_item_id: str,
    *,
    body: PatchApiPlaylistItemsPlaylistItemIdBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/api/playlist_items/{playlist_item_id}".format(
            playlist_item_id=quote(str(playlist_item_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/vnd.api+json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PatchApiPlaylistItemsPlaylistItemIdResponse200 | None:
    if response.status_code == 200:
        response_200 = PatchApiPlaylistItemsPlaylistItemIdResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PatchApiPlaylistItemsPlaylistItemIdResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    playlist_item_id: str,
    *,
    client: AuthenticatedClient,
    body: PatchApiPlaylistItemsPlaylistItemIdBody,
) -> Response[PatchApiPlaylistItemsPlaylistItemIdResponse200]:
    """Update playlist item position

     **Host**: http://production.lightphonecloud.com

    Args:
        playlist_item_id (str):
        body (PatchApiPlaylistItemsPlaylistItemIdBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PatchApiPlaylistItemsPlaylistItemIdResponse200]
    """

    kwargs = _get_kwargs(
        playlist_item_id=playlist_item_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    playlist_item_id: str,
    *,
    client: AuthenticatedClient,
    body: PatchApiPlaylistItemsPlaylistItemIdBody,
) -> PatchApiPlaylistItemsPlaylistItemIdResponse200 | None:
    """Update playlist item position

     **Host**: http://production.lightphonecloud.com

    Args:
        playlist_item_id (str):
        body (PatchApiPlaylistItemsPlaylistItemIdBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PatchApiPlaylistItemsPlaylistItemIdResponse200
    """

    return sync_detailed(
        playlist_item_id=playlist_item_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    playlist_item_id: str,
    *,
    client: AuthenticatedClient,
    body: PatchApiPlaylistItemsPlaylistItemIdBody,
) -> Response[PatchApiPlaylistItemsPlaylistItemIdResponse200]:
    """Update playlist item position

     **Host**: http://production.lightphonecloud.com

    Args:
        playlist_item_id (str):
        body (PatchApiPlaylistItemsPlaylistItemIdBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PatchApiPlaylistItemsPlaylistItemIdResponse200]
    """

    kwargs = _get_kwargs(
        playlist_item_id=playlist_item_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    playlist_item_id: str,
    *,
    client: AuthenticatedClient,
    body: PatchApiPlaylistItemsPlaylistItemIdBody,
) -> PatchApiPlaylistItemsPlaylistItemIdResponse200 | None:
    """Update playlist item position

     **Host**: http://production.lightphonecloud.com

    Args:
        playlist_item_id (str):
        body (PatchApiPlaylistItemsPlaylistItemIdBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PatchApiPlaylistItemsPlaylistItemIdResponse200
    """

    return (
        await asyncio_detailed(
            playlist_item_id=playlist_item_id,
            client=client,
            body=body,
        )
    ).parsed
