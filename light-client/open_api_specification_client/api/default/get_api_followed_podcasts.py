from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_api_followed_podcasts_response_200 import GetApiFollowedPodcastsResponse200
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
        "url": "/api/followed_podcasts",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetApiFollowedPodcastsResponse200 | None:
    if response.status_code == 200:
        response_200 = GetApiFollowedPodcastsResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetApiFollowedPodcastsResponse200]:
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
) -> Response[GetApiFollowedPodcastsResponse200]:
    """/api/followed_podcasts

     **Host**: http://production.lightphonecloud.com

    Args:
        device_tool_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiFollowedPodcastsResponse200]
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
) -> GetApiFollowedPodcastsResponse200 | None:
    """/api/followed_podcasts

     **Host**: http://production.lightphonecloud.com

    Args:
        device_tool_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiFollowedPodcastsResponse200
    """

    return sync_detailed(
        client=client,
        device_tool_id=device_tool_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    device_tool_id: str | Unset = UNSET,
) -> Response[GetApiFollowedPodcastsResponse200]:
    """/api/followed_podcasts

     **Host**: http://production.lightphonecloud.com

    Args:
        device_tool_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiFollowedPodcastsResponse200]
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
) -> GetApiFollowedPodcastsResponse200 | None:
    """/api/followed_podcasts

     **Host**: http://production.lightphonecloud.com

    Args:
        device_tool_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiFollowedPodcastsResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            device_tool_id=device_tool_id,
        )
    ).parsed
