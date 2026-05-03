from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_api_tools_param_2_response_200 import GetApiToolsParam2Response200
from ...types import Response


def _get_kwargs(
    param2: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/tools/{param2}".format(
            param2=quote(str(param2), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetApiToolsParam2Response200 | None:
    if response.status_code == 200:
        response_200 = GetApiToolsParam2Response200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetApiToolsParam2Response200]:
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
) -> Response[GetApiToolsParam2Response200]:
    """/api/tools/:param2

     **Host**: http://production.lightphonecloud.com

    Args:
        param2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiToolsParam2Response200]
    """

    kwargs = _get_kwargs(
        param2=param2,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    param2: str,
    *,
    client: AuthenticatedClient,
) -> GetApiToolsParam2Response200 | None:
    """/api/tools/:param2

     **Host**: http://production.lightphonecloud.com

    Args:
        param2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiToolsParam2Response200
    """

    return sync_detailed(
        param2=param2,
        client=client,
    ).parsed


async def asyncio_detailed(
    param2: str,
    *,
    client: AuthenticatedClient,
) -> Response[GetApiToolsParam2Response200]:
    """/api/tools/:param2

     **Host**: http://production.lightphonecloud.com

    Args:
        param2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiToolsParam2Response200]
    """

    kwargs = _get_kwargs(
        param2=param2,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    param2: str,
    *,
    client: AuthenticatedClient,
) -> GetApiToolsParam2Response200 | None:
    """/api/tools/:param2

     **Host**: http://production.lightphonecloud.com

    Args:
        param2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiToolsParam2Response200
    """

    return (
        await asyncio_detailed(
            param2=param2,
            client=client,
        )
    ).parsed
