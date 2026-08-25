from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.patch_api_contacts_v2_contact_id_body import PatchApiContactsV2ContactIdBody
from ...models.patch_api_contacts_v2_contact_id_response_200 import PatchApiContactsV2ContactIdResponse200
from ...types import Response


def _get_kwargs(
    contact_id: str,
    *,
    body: PatchApiContactsV2ContactIdBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/api/contacts_v2/{contact_id}".format(
            contact_id=quote(str(contact_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/vnd.api+json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PatchApiContactsV2ContactIdResponse200 | None:
    if response.status_code == 200:
        response_200 = PatchApiContactsV2ContactIdResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PatchApiContactsV2ContactIdResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    contact_id: str,
    *,
    client: AuthenticatedClient,
    body: PatchApiContactsV2ContactIdBody,
) -> Response[PatchApiContactsV2ContactIdResponse200]:
    """Update a contact

     **Host**: http://production.lightphonecloud.com

    Args:
        contact_id (str):
        body (PatchApiContactsV2ContactIdBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PatchApiContactsV2ContactIdResponse200]
    """

    kwargs = _get_kwargs(
        contact_id=contact_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    contact_id: str,
    *,
    client: AuthenticatedClient,
    body: PatchApiContactsV2ContactIdBody,
) -> PatchApiContactsV2ContactIdResponse200 | None:
    """Update a contact

     **Host**: http://production.lightphonecloud.com

    Args:
        contact_id (str):
        body (PatchApiContactsV2ContactIdBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PatchApiContactsV2ContactIdResponse200
    """

    return sync_detailed(
        contact_id=contact_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    contact_id: str,
    *,
    client: AuthenticatedClient,
    body: PatchApiContactsV2ContactIdBody,
) -> Response[PatchApiContactsV2ContactIdResponse200]:
    """Update a contact

     **Host**: http://production.lightphonecloud.com

    Args:
        contact_id (str):
        body (PatchApiContactsV2ContactIdBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PatchApiContactsV2ContactIdResponse200]
    """

    kwargs = _get_kwargs(
        contact_id=contact_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    contact_id: str,
    *,
    client: AuthenticatedClient,
    body: PatchApiContactsV2ContactIdBody,
) -> PatchApiContactsV2ContactIdResponse200 | None:
    """Update a contact

     **Host**: http://production.lightphonecloud.com

    Args:
        contact_id (str):
        body (PatchApiContactsV2ContactIdBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PatchApiContactsV2ContactIdResponse200
    """

    return (
        await asyncio_detailed(
            contact_id=contact_id,
            client=client,
            body=body,
        )
    ).parsed
