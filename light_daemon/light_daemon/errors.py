"""Map API failures to gRPC status codes.

The API only raises bare RuntimeErrors and httpx errors.

httpx errors -> DEADLINE_EXCEEDED / UNAVAILABLE.

For RuntimeErrors: disambiguate based on the error message.
1. auth keywords detected   -> UNAUTHENTICATED
2. trailing HTTP status     -> follow _STATUS_MAP (5xx: UNAVAILABLE, 404: NOT_FOUND, ...)
3. "no <x> found" keyword   -> NOT_FOUND
4. else                     -> FAILED_PRECONDITION

Anything else that isn't RuntimeError -> INTERNAL.
"""

from __future__ import annotations

import re
from contextlib import contextmanager
from typing import Any, Iterator

import grpc
import httpx

_AUTH_HINTS = ("credential", "cached session", "log in", "login", "password")
_NOT_FOUND_HINTS = ("no device found", "no tool found", "no installed tool")

# _ensure_ok(...) -> RuntimeError("Get tracks: 503")
_TRAILING_STATUS = re.compile(r":\s*(\d{3})\s*$")

_STATUS_MAP = {
    400: grpc.StatusCode.INVALID_ARGUMENT,
    401: grpc.StatusCode.UNAUTHENTICATED,
    403: grpc.StatusCode.PERMISSION_DENIED,
    404: grpc.StatusCode.NOT_FOUND,
    409: grpc.StatusCode.ABORTED,
    429: grpc.StatusCode.UNAVAILABLE,
}


def _looks_like_auth(message: str) -> bool:
    lowered = message.lower()
    return any(hint in lowered for hint in _AUTH_HINTS)


def _code_from_http_status(message: str) -> grpc.StatusCode | None:
    m = _TRAILING_STATUS.search(message)
    if m is None:
        return None
    http = int(m.group(1))
    if http in _STATUS_MAP:
        return _STATUS_MAP[http]
    if 500 <= http <= 599:
        return grpc.StatusCode.UNAVAILABLE  # transient upstream failure; safe to retry
    if 400 <= http <= 499:
        return grpc.StatusCode.FAILED_PRECONDITION
    return None


def _runtime_error_code(message: str) -> grpc.StatusCode:
    if _looks_like_auth(message):
        return grpc.StatusCode.UNAUTHENTICATED
    mapped = _code_from_http_status(message)
    if mapped is not None:
        return mapped
    if any(hint in message.lower() for hint in _NOT_FOUND_HINTS):
        return grpc.StatusCode.NOT_FOUND
    return grpc.StatusCode.FAILED_PRECONDITION


@contextmanager
def grpc_errors(context: Any) -> Iterator[None]:
    """Run a servicer body; translate any `light_api` failure into `context.abort`."""
    try:
        yield
    except httpx.TimeoutException as e:
        context.abort(grpc.StatusCode.DEADLINE_EXCEEDED, f"Light API timed out: {e}")
    except httpx.HTTPError as e:
        context.abort(grpc.StatusCode.UNAVAILABLE, f"Light API unreachable: {e}")
    except RuntimeError as e:
        context.abort(_runtime_error_code(str(e)), str(e))
    except Exception as e:  # noqa: BLE001 - last-resort catch-all
        context.abort(grpc.StatusCode.INTERNAL, f"{type(e).__name__}: {e}")
