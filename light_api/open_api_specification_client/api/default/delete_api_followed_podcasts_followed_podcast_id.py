from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_api_followed_podcasts_followed_podcast_id_response_200 import (
    DeleteApiFollowedPodcastsFollowedPodcastIdResponse200,
)
from ...types import Response


def _get_kwargs(
    followed_podcast_id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/api/followed_podcasts/{followed_podcast_id}".format(
            followed_podcast_id=quote(str(followed_podcast_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DeleteApiFollowedPodcastsFollowedPodcastIdResponse200 | None:
    if response.status_code == 200:
        response_200 = DeleteApiFollowedPodcastsFollowedPodcastIdResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[DeleteApiFollowedPodcastsFollowedPodcastIdResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    followed_podcast_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[DeleteApiFollowedPodcastsFollowedPodcastIdResponse200]:
    """Unfollow a podcast

     **Host**: http://production.lightphonecloud.com

    Args:
        followed_podcast_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteApiFollowedPodcastsFollowedPodcastIdResponse200]
    """

    kwargs = _get_kwargs(
        followed_podcast_id=followed_podcast_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    followed_podcast_id: str,
    *,
    client: AuthenticatedClient,
) -> DeleteApiFollowedPodcastsFollowedPodcastIdResponse200 | None:
    """Unfollow a podcast

     **Host**: http://production.lightphonecloud.com

    Args:
        followed_podcast_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteApiFollowedPodcastsFollowedPodcastIdResponse200
    """

    return sync_detailed(
        followed_podcast_id=followed_podcast_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    followed_podcast_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[DeleteApiFollowedPodcastsFollowedPodcastIdResponse200]:
    """Unfollow a podcast

     **Host**: http://production.lightphonecloud.com

    Args:
        followed_podcast_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteApiFollowedPodcastsFollowedPodcastIdResponse200]
    """

    kwargs = _get_kwargs(
        followed_podcast_id=followed_podcast_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    followed_podcast_id: str,
    *,
    client: AuthenticatedClient,
) -> DeleteApiFollowedPodcastsFollowedPodcastIdResponse200 | None:
    """Unfollow a podcast

     **Host**: http://production.lightphonecloud.com

    Args:
        followed_podcast_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteApiFollowedPodcastsFollowedPodcastIdResponse200
    """

    return (
        await asyncio_detailed(
            followed_podcast_id=followed_podcast_id,
            client=client,
        )
    ).parsed
