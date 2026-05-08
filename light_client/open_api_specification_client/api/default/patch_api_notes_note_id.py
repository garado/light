from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.patch_api_notes_note_id_body import PatchApiNotesNoteIdBody
from ...models.patch_api_notes_note_id_response_200 import PatchApiNotesNoteIdResponse200
from ...types import Response


def _get_kwargs(
    note_id: str,
    *,
    body: PatchApiNotesNoteIdBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/api/notes/{note_id}".format(
            note_id=quote(str(note_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/vnd.api+json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PatchApiNotesNoteIdResponse200 | None:
    if response.status_code == 200:
        response_200 = PatchApiNotesNoteIdResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PatchApiNotesNoteIdResponse200]:
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
    body: PatchApiNotesNoteIdBody,
) -> Response[PatchApiNotesNoteIdResponse200]:
    """Update note metadata

     **Host**: http://production.lightphonecloud.com

    Update attributes of an existing note.

    Args:
        note_id (str):
        body (PatchApiNotesNoteIdBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PatchApiNotesNoteIdResponse200]
    """

    kwargs = _get_kwargs(
        note_id=note_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    note_id: str,
    *,
    client: AuthenticatedClient,
    body: PatchApiNotesNoteIdBody,
) -> PatchApiNotesNoteIdResponse200 | None:
    """Update note metadata

     **Host**: http://production.lightphonecloud.com

    Update attributes of an existing note.

    Args:
        note_id (str):
        body (PatchApiNotesNoteIdBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PatchApiNotesNoteIdResponse200
    """

    return sync_detailed(
        note_id=note_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    note_id: str,
    *,
    client: AuthenticatedClient,
    body: PatchApiNotesNoteIdBody,
) -> Response[PatchApiNotesNoteIdResponse200]:
    """Update note metadata

     **Host**: http://production.lightphonecloud.com

    Update attributes of an existing note.

    Args:
        note_id (str):
        body (PatchApiNotesNoteIdBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PatchApiNotesNoteIdResponse200]
    """

    kwargs = _get_kwargs(
        note_id=note_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    note_id: str,
    *,
    client: AuthenticatedClient,
    body: PatchApiNotesNoteIdBody,
) -> PatchApiNotesNoteIdResponse200 | None:
    """Update note metadata

     **Host**: http://production.lightphonecloud.com

    Update attributes of an existing note.

    Args:
        note_id (str):
        body (PatchApiNotesNoteIdBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PatchApiNotesNoteIdResponse200
    """

    return (
        await asyncio_detailed(
            note_id=note_id,
            client=client,
            body=body,
        )
    ).parsed
