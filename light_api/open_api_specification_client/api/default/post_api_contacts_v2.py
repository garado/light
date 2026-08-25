from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_api_contacts_v2_body import PostApiContactsV2Body
from ...models.post_api_contacts_v2_response_201 import PostApiContactsV2Response201
from ...types import Response


def _get_kwargs(
    *,
    body: PostApiContactsV2Body,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/contacts_v2",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/vnd.api+json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PostApiContactsV2Response201 | None:
    if response.status_code == 201:
        response_201 = PostApiContactsV2Response201.from_dict(response.json())

        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PostApiContactsV2Response201]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: PostApiContactsV2Body,
) -> Response[PostApiContactsV2Response201]:
    """Add a contact

     **Host**: http://production.lightphonecloud.com

    Args:
        body (PostApiContactsV2Body):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostApiContactsV2Response201]
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
    body: PostApiContactsV2Body,
) -> PostApiContactsV2Response201 | None:
    """Add a contact

     **Host**: http://production.lightphonecloud.com

    Args:
        body (PostApiContactsV2Body):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostApiContactsV2Response201
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: PostApiContactsV2Body,
) -> Response[PostApiContactsV2Response201]:
    """Add a contact

     **Host**: http://production.lightphonecloud.com

    Args:
        body (PostApiContactsV2Body):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostApiContactsV2Response201]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: PostApiContactsV2Body,
) -> PostApiContactsV2Response201 | None:
    """Add a contact

     **Host**: http://production.lightphonecloud.com

    Args:
        body (PostApiContactsV2Body):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostApiContactsV2Response201
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
