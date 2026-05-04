from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_api_notes_note_id_response_200 import GetApiNotesNoteIdResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    note_id: str,
    *,
    device_tool_id: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["device_tool_id"] = device_tool_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/notes/{note_id}".format(
            note_id=quote(str(note_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetApiNotesNoteIdResponse200 | None:
    if response.status_code == 200:
        response_200 = GetApiNotesNoteIdResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetApiNotesNoteIdResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    note_id: str,
    *,
    client: AuthenticatedClient,
    device_tool_id: str | Unset = UNSET,
) -> Response[GetApiNotesNoteIdResponse200]:
    """/api/notes/:note_id

     **Host**: http://production.lightphonecloud.com

    Fetch metadata for a single note.

    Args:
        note_id (str):
        device_tool_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiNotesNoteIdResponse200]
    """

    kwargs = _get_kwargs(
        note_id=note_id,
        device_tool_id=device_tool_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    note_id: str,
    *,
    client: AuthenticatedClient,
    device_tool_id: str | Unset = UNSET,
) -> GetApiNotesNoteIdResponse200 | None:
    """/api/notes/:note_id

     **Host**: http://production.lightphonecloud.com

    Fetch metadata for a single note.

    Args:
        note_id (str):
        device_tool_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiNotesNoteIdResponse200
    """

    return sync_detailed(
        note_id=note_id,
        client=client,
        device_tool_id=device_tool_id,
    ).parsed


async def asyncio_detailed(
    note_id: str,
    *,
    client: AuthenticatedClient,
    device_tool_id: str | Unset = UNSET,
) -> Response[GetApiNotesNoteIdResponse200]:
    """/api/notes/:note_id

     **Host**: http://production.lightphonecloud.com

    Fetch metadata for a single note.

    Args:
        note_id (str):
        device_tool_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiNotesNoteIdResponse200]
    """

    kwargs = _get_kwargs(
        note_id=note_id,
        device_tool_id=device_tool_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    note_id: str,
    *,
    client: AuthenticatedClient,
    device_tool_id: str | Unset = UNSET,
) -> GetApiNotesNoteIdResponse200 | None:
    """/api/notes/:note_id

     **Host**: http://production.lightphonecloud.com

    Fetch metadata for a single note.

    Args:
        note_id (str):
        device_tool_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiNotesNoteIdResponse200
    """

    return (
        await asyncio_detailed(
            note_id=note_id,
            client=client,
            device_tool_id=device_tool_id,
        )
    ).parsed
