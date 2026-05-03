from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.patch_api_audios_param_2_body import PatchApiAudiosParam2Body
from ...models.patch_api_audios_param_2_response_200 import PatchApiAudiosParam2Response200
from ...types import Response


def _get_kwargs(
    param2: str,
    *,
    body: PatchApiAudiosParam2Body,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/api/audios/{param2}".format(
            param2=quote(str(param2), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/vnd.api+json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PatchApiAudiosParam2Response200 | None:
    if response.status_code == 200:
        response_200 = PatchApiAudiosParam2Response200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PatchApiAudiosParam2Response200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    param2: str,
    *,
    client: AuthenticatedClient,
    body: PatchApiAudiosParam2Body,
) -> Response[PatchApiAudiosParam2Response200]:
    """/api/audios/:param2

     **Host**: http://production.lightphonecloud.com

    Args:
        param2 (str):
        body (PatchApiAudiosParam2Body):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PatchApiAudiosParam2Response200]
    """

    kwargs = _get_kwargs(
        param2=param2,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    param2: str,
    *,
    client: AuthenticatedClient,
    body: PatchApiAudiosParam2Body,
) -> PatchApiAudiosParam2Response200 | None:
    """/api/audios/:param2

     **Host**: http://production.lightphonecloud.com

    Args:
        param2 (str):
        body (PatchApiAudiosParam2Body):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PatchApiAudiosParam2Response200
    """

    return sync_detailed(
        param2=param2,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    param2: str,
    *,
    client: AuthenticatedClient,
    body: PatchApiAudiosParam2Body,
) -> Response[PatchApiAudiosParam2Response200]:
    """/api/audios/:param2

     **Host**: http://production.lightphonecloud.com

    Args:
        param2 (str):
        body (PatchApiAudiosParam2Body):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PatchApiAudiosParam2Response200]
    """

    kwargs = _get_kwargs(
        param2=param2,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    param2: str,
    *,
    client: AuthenticatedClient,
    body: PatchApiAudiosParam2Body,
) -> PatchApiAudiosParam2Response200 | None:
    """/api/audios/:param2

     **Host**: http://production.lightphonecloud.com

    Args:
        param2 (str):
        body (PatchApiAudiosParam2Body):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PatchApiAudiosParam2Response200
    """

    return (
        await asyncio_detailed(
            param2=param2,
            client=client,
            body=body,
        )
    ).parsed
