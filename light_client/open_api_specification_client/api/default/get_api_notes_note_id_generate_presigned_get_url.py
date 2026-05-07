from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_api_notes_note_id_generate_presigned_get_url_response_200 import (
    GetApiNotesNoteIdGeneratePresignedGetUrlResponse200,
)
from ...types import Response


def _get_kwargs(
    note_id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/notes/{note_id}/generate_presigned_get_url".format(
            note_id=quote(str(note_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetApiNotesNoteIdGeneratePresignedGetUrlResponse200 | None:
    if response.status_code == 200:
        response_200 = GetApiNotesNoteIdGeneratePresignedGetUrlResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetApiNotesNoteIdGeneratePresignedGetUrlResponse200]:
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
) -> Response[GetApiNotesNoteIdGeneratePresignedGetUrlResponse200]:
    """Generate presigned download URL for a note

     **Host**: http://production.lightphonecloud.com

    Args:
        note_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiNotesNoteIdGeneratePresignedGetUrlResponse200]
    """

    kwargs = _get_kwargs(
        note_id=note_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    note_id: str,
    *,
    client: AuthenticatedClient,
) -> GetApiNotesNoteIdGeneratePresignedGetUrlResponse200 | None:
    """Generate presigned download URL for a note

     **Host**: http://production.lightphonecloud.com

    Args:
        note_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiNotesNoteIdGeneratePresignedGetUrlResponse200
    """

    return sync_detailed(
        note_id=note_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    note_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[GetApiNotesNoteIdGeneratePresignedGetUrlResponse200]:
    """Generate presigned download URL for a note

     **Host**: http://production.lightphonecloud.com

    Args:
        note_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiNotesNoteIdGeneratePresignedGetUrlResponse200]
    """

    kwargs = _get_kwargs(
        note_id=note_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    note_id: str,
    *,
    client: AuthenticatedClient,
) -> GetApiNotesNoteIdGeneratePresignedGetUrlResponse200 | None:
    """Generate presigned download URL for a note

     **Host**: http://production.lightphonecloud.com

    Args:
        note_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiNotesNoteIdGeneratePresignedGetUrlResponse200
    """

    return (
        await asyncio_detailed(
            note_id=note_id,
            client=client,
        )
    ).parsed
