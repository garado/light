"""Run a `Light` session on a dedicated background thread.

`Light` is not thread-safe, so any consumer with multiple threads - a TUI event loop,
a gRPC threadpool - must funnel every call through a single owner.

`LightThread` is that owner: `submit(fn)` hands `fn(light)` to the worker thread and
blocks for the result.
"""

from __future__ import annotations

import queue
import threading
from concurrent.futures import Future
from dataclasses import dataclass
from typing import Any, Callable

from light_api.client import Light


@dataclass
class LightConfig:
    """Everything needed to construct a `Light` session.

    Mirrors `Light.__init__`; unset fields fall back to files/env/keyring exactly as they do there.
    """

    email: str | None = None
    email_file: str | None = None
    password: str | None = None
    password_file: str | None = None
    phone: str | None = None
    phone_file: str | None = None
    device_id: str | None = None
    device_id_file: str | None = None
    cache_enabled: bool = False
    password_prompt: Callable[[], str] | None = None


class LightThread:
    """Owns a `Light` instance on a background thread. Work is submitted via `submit`."""

    def __init__(self, config: LightConfig) -> None:
        """Initialize the thread."""
        self._config = config

        # queue of work to do
        self._queue: queue.Queue[tuple[Callable[[Light], Any], Future[Any]] | None] = (
            queue.Queue()
        )

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._ready = threading.Event()
        self._error: BaseException | None = None
        self._lock = threading.Lock()
        self._stopped = False

    def start(self) -> None:
        """Start the thread and block until the session finishes its auth attempt.

        Raises:
            Whatever the session setup raised (bad credentials, network, ...)
        """
        self._thread.start()
        self._ready.wait()
        if self._error is not None:
            raise self._error

    def _run(self) -> None:
        try:
            with Light(
                email=self._config.email,
                email_file=self._config.email_file,
                password=self._config.password,
                password_file=self._config.password_file,
                phone=self._config.phone,
                phone_file=self._config.phone_file,
                device_id=self._config.device_id,
                device_id_file=self._config.device_id_file,
                cache_enabled=self._config.cache_enabled,
                password_prompt=self._config.password_prompt,
            ) as light:
                self._ready.set()
                while True:
                    item = self._queue.get()
                    if item is None:
                        break
                    func, future = item
                    try:
                        future.set_result(func(light))
                    except BaseException as e:
                        future.set_exception(e)
        except BaseException as e:
            self._error = e
            self._ready.set()
        finally:
            self._fail_pending()

    def _fail_pending(self) -> None:
        """Empties queue (fails pending items) when worker is done to prevent callers from hanging."""
        with self._lock:
            self._stopped = True
            while True:
                try:
                    item = self._queue.get_nowait()
                except queue.Empty:
                    break

                if item is not None:
                    _, future = item
                    if not future.done():
                        future.set_exception(
                            RuntimeError("LightThread worker has stopped")
                        )

    def submit(self, func: Callable[[Light], Any], timeout: float | None = None) -> Any:
        """Run `func(light)` on the worker thread and return its result (blocking).

        Raises:
            - RuntimeError if the worker is not running
            - TimeoutError if `timeout` elapses first
            - Or whatever `func` raised.
        """
        future: Future[Any] = Future()
        with self._lock:
            if self._stopped:
                raise RuntimeError("LightThread worker is not running")
            self._queue.put((func, future))
        return future.result(timeout)

    def shutdown(self, timeout: float | None = 5.0) -> None:
        """Ask the worker to stop and wait (up to `timeout` seconds) for it to exit."""
        self._queue.put(None)
        self._thread.join(timeout)
