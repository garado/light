"""Background thread that runs a Light session, fed by a queue from the UI thread."""

import queue
import threading
from concurrent.futures import Future
from dataclasses import dataclass
from typing import Any, Callable

from light_api.client import Light


@dataclass
class LightConfig:
    email: str | None = None
    email_file: str | None = None
    password: str | None = None
    password_file: str | None = None
    phone: str | None = None
    phone_file: str | None = None
    device_id: str | None = None
    device_id_file: str | None = None
    cache_enabled: bool = False


class LightThread:
    """Runs a Light instance in a dedicated background thread."""

    def __init__(self, config: LightConfig) -> None:
        self._config = config
        self._queue: queue.Queue[tuple[Callable[[Light], Any], Future[Any]] | None] = (
            queue.Queue()
        )
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._ready = threading.Event()
        self._error: BaseException | None = None

    def start(self) -> None:
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
            ) as light:
                self._ready.set()
                while True:
                    item = self._queue.get()
                    if item is None:
                        break
                    func, future = item
                    try:
                        future.set_result(func(light))
                    except Exception as e:
                        future.set_exception(e)
        except BaseException as e:
            self._error = e
            self._ready.set()

    def submit(self, func: Callable[[Light], Any]) -> Any:
        future: Future[Any] = Future()
        self._queue.put((func, future))
        return future.result()

    def shutdown(self) -> None:
        self._queue.put(None)
        self._thread.join()
