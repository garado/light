"""Rate limiting + retry for outbound HTTP.

Everything that talks to the Light API (and to the presigned S3 URLs it hands
out) goes through :class:`RetryTransport`, an ``httpx`` transport that:

- paces requests through a process-wide token bucket so a bulk operation
  (e.g. uploading a whole music library) can't hammer the API, and
- retries transient failures - HTTP 429 and 5xx, plus connection/read errors
  where no response came back - with exponential backoff and jitter,
  honoring a ``Retry-After`` header when the server sends one.

Retries are only attempted when replaying the request is safe:

- GET/HEAD/PUT/DELETE/OPTIONS are idempotent, so any retryable status is fair
  game.
- POST is only retried on 429 or on a connection error where the server
  demonstrably never received a full request, so a create can't be
  duplicated.
- A request with a streaming body (the chunked music upload) is never
  retried, since its body generator is already spent.

Generated API calls pick this up via ``AuthenticatedClient(httpx_args=...)``;
raw one-off calls should go through :func:`http_request` instead of
``httpx.request``.
"""

from __future__ import annotations

import email.utils
import logging
import random
import threading
import time

from datetime import datetime, timezone
from typing import Any

import httpx

log = logging.getLogger(f"light.{__name__}")

# Token bucket: sustained rate and the burst it will let through after an idle
# period. Shared across every client in the process.
REQUESTS_PER_SECOND = 5.0
RATE_LIMIT_BURST = 10

# Total attempts = 1 + MAX_RETRIES.
MAX_RETRIES = 3

# Statuses worth retrying (for a replayable request).
RETRY_STATUS_CODES = frozenset({429, 500, 502, 503, 504})

# Methods we consider safe to replay on any retryable status.
IDEMPOTENT_METHODS = frozenset({"GET", "HEAD", "PUT", "DELETE", "OPTIONS"})

BACKOFF_BASE_SECONDS = 0.5
BACKOFF_MAX_SECONDS = 30.0

# Default per-request timeout for http_request().
DEFAULT_TIMEOUT_SECONDS = 30.0


class _TokenBucket:
    """Thread-safe token bucket. ``acquire()`` blocks until a token is free."""

    def __init__(self, rate: float, capacity: int) -> None:
        self._rate = rate
        self._capacity = float(capacity)
        self._tokens = float(capacity)
        self._updated = time.monotonic()
        self._lock = threading.Lock()

    def acquire(self) -> None:
        while True:
            with self._lock:
                now = time.monotonic()
                self._tokens = min(
                    self._capacity,
                    self._tokens + (now - self._updated) * self._rate,
                )
                self._updated = now
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return
                wait = (1.0 - self._tokens) / self._rate
            time.sleep(wait)


_RATE_LIMITER = _TokenBucket(REQUESTS_PER_SECOND, RATE_LIMIT_BURST)


def _is_replayable(request: httpx.Request) -> bool:
    """True if the request body has been buffered and can be sent again."""
    try:
        request.content
    except httpx.RequestNotRead:
        return False
    return True


def _should_retry_response(
    method: str, response: httpx.Response, replayable: bool
) -> bool:
    if not replayable or response.status_code not in RETRY_STATUS_CODES:
        return False
    if response.status_code == 429:
        return True
    return method in IDEMPOTENT_METHODS


def _parse_retry_after(value: str | None) -> float | None:
    """Parse a ``Retry-After`` header (delta-seconds or HTTP-date) to seconds."""
    if not value:
        return None
    value = value.strip()
    if value.isdigit():
        return float(value)
    try:
        when = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if when is None:
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return max(0.0, (when - datetime.now(timezone.utc)).total_seconds())


def _backoff_delay(attempt: int, retry_after: float | None) -> float:
    """Seconds to wait before the next attempt (0-indexed)."""
    if retry_after is not None:
        return min(retry_after, BACKOFF_MAX_SECONDS)
    ceiling = min(BACKOFF_BASE_SECONDS * (2**attempt), BACKOFF_MAX_SECONDS)
    # Full jitter over the lower half..full window.
    return ceiling * (0.5 + random.random() / 2)


class RetryTransport(httpx.BaseTransport):
    """Wraps another transport with the token bucket and the retry loop."""

    def __init__(
        self,
        wrapped: httpx.BaseTransport | None = None,
        limiter: _TokenBucket | None = None,
    ) -> None:
        self._wrapped = wrapped if wrapped is not None else httpx.HTTPTransport()
        self._limiter = limiter if limiter is not None else _RATE_LIMITER

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        method = request.method.upper()
        replayable = _is_replayable(request)

        for attempt in range(MAX_RETRIES + 1):
            self._limiter.acquire()
            last = attempt == MAX_RETRIES

            try:
                response = self._wrapped.handle_request(request)
            except httpx.TransportError as exc:
                # No response means the server may never have seen a complete
                # request, so replaying is safe for any method.
                if last or not replayable:
                    raise
                delay = _backoff_delay(attempt, None)
                log.warning(
                    "%s %s failed (%s); retrying in %.1fs (attempt %d/%d)",
                    method,
                    request.url,
                    exc.__class__.__name__,
                    delay,
                    attempt + 1,
                    MAX_RETRIES,
                )
                time.sleep(delay)
                continue

            if last or not _should_retry_response(method, response, replayable):
                return response

            retry_after = _parse_retry_after(response.headers.get("Retry-After"))
            status = response.status_code
            response.close()
            delay = _backoff_delay(attempt, retry_after)
            log.warning(
                "%s %s -> %d; retrying in %.1fs (attempt %d/%d)",
                method,
                request.url,
                status,
                delay,
                attempt + 1,
                MAX_RETRIES,
            )
            time.sleep(delay)

        return response  # pragma: no cover - loop always returns or raises

    def close(self) -> None:
        self._wrapped.close()


def httpx_args() -> dict[str, Any]:
    """Kwargs for ``AuthenticatedClient(httpx_args=...)`` / ``Client(...)``."""
    return {"transport": RetryTransport()}


def http_request(
    method: str,
    url: str,
    *,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    **kwargs: Any,
) -> httpx.Response:
    """Drop-in for ``httpx.request`` that goes through :class:`RetryTransport`."""
    with httpx.Client(transport=RetryTransport(), timeout=timeout) as client:
        return client.request(method, url, **kwargs)
