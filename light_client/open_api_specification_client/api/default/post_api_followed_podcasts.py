from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_api_followed_podcasts_body import PostApiFollowedPodcastsBody
from ...models.post_api_followed_podcasts_response_201 import PostApiFollowedPodcastsResponse201
from ...types import Response


def _get_kwargs(
    *,
    body: PostApiFollowedPodcastsBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/followed_podcasts",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/vnd.api+json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PostApiFollowedPodcastsResponse201 | None:
    if response.status_code == 201:
        response_201 = PostApiFollowedPodcastsResponse201.from_dict(response.json())

        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PostApiFollowedPodcastsResponse201]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: PostApiFollowedPodcastsBody,
) -> Response[PostApiFollowedPodcastsResponse201]:
    """Follow a podcast

     **Host**: http://production.lightphonecloud.com

    Args:
        body (PostApiFollowedPodcastsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostApiFollowedPodcastsResponse201]
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
    body: PostApiFollowedPodcastsBody,
) -> PostApiFollowedPodcastsResponse201 | None:
    """Follow a podcast

     **Host**: http://production.lightphonecloud.com

    Args:
        body (PostApiFollowedPodcastsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostApiFollowedPodcastsResponse201
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: PostApiFollowedPodcastsBody,
) -> Response[PostApiFollowedPodcastsResponse201]:
    """Follow a podcast

     **Host**: http://production.lightphonecloud.com

    Args:
        body (PostApiFollowedPodcastsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostApiFollowedPodcastsResponse201]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: PostApiFollowedPodcastsBody,
) -> PostApiFollowedPodcastsResponse201 | None:
    """Follow a podcast

     **Host**: http://production.lightphonecloud.com

    Args:
        body (PostApiFollowedPodcastsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostApiFollowedPodcastsResponse201
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
