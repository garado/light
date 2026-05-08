from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_api_playlists_sort_mode_body import PostApiPlaylistsSortModeBody
from ...models.post_api_playlists_sort_mode_response_400 import PostApiPlaylistsSortModeResponse400
from ...types import Response


def _get_kwargs(
    *,
    body: PostApiPlaylistsSortModeBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/playlists/sort_mode",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/vnd.api+json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PostApiPlaylistsSortModeResponse400 | None:
    if response.status_code == 400:
        response_400 = PostApiPlaylistsSortModeResponse400.from_dict(response.json())

        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PostApiPlaylistsSortModeResponse400]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: PostApiPlaylistsSortModeBody,
) -> Response[PostApiPlaylistsSortModeResponse400]:
    """Set playlist sort mode

     **Host**: http://production.lightphonecloud.com

    Args:
        body (PostApiPlaylistsSortModeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostApiPlaylistsSortModeResponse400]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: PostApiPlaylistsSortModeBody,
) -> PostApiPlaylistsSortModeResponse400 | None:
    """Set playlist sort mode

     **Host**: http://production.lightphonecloud.com

    Args:
        body (PostApiPlaylistsSortModeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostApiPlaylistsSortModeResponse400
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: PostApiPlaylistsSortModeBody,
) -> Response[PostApiPlaylistsSortModeResponse400]:
    """Set playlist sort mode

     **Host**: http://production.lightphonecloud.com

    Args:
        body (PostApiPlaylistsSortModeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostApiPlaylistsSortModeResponse400]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: PostApiPlaylistsSortModeBody,
) -> PostApiPlaylistsSortModeResponse400 | None:
    """Set playlist sort mode

     **Host**: http://production.lightphonecloud.com

    Args:
        body (PostApiPlaylistsSortModeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostApiPlaylistsSortModeResponse400
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
