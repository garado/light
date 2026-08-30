"""Map API failures to gRPC status codes."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

import grpc
import httpx

_AUTH_HINTS = ("credential", "cached session", "log in", "login", "password")


def _looks_like_auth(message: str) -> bool:
    lowered = message.lower()
    return any(hint in lowered for hint in _AUTH_HINTS)


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
        if _looks_like_auth(str(e)):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, str(e))
        context.abort(grpc.StatusCode.FAILED_PRECONDITION, str(e))
    except Exception as e:  # noqa: BLE001 - last-resort catch-all
        context.abort(grpc.StatusCode.INTERNAL, f"{type(e).__name__}: {e}")
