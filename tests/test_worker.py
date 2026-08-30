"""LightThread: a failing / slow / post-shutdown call must never wedge submit()."""

import time
from concurrent.futures import Future

import pytest

from light_api.worker import LightConfig, LightThread


class _FakeLightCM:
    """Stand-in for `Light` as a context manager - no network, no auth."""

    def __init__(self, **_kwargs):
        pass

    def __enter__(self):
        return object()

    def __exit__(self, *_exc):
        return False


@pytest.fixture
def worker(monkeypatch):
    monkeypatch.setattr("light_api.worker.Light", _FakeLightCM)
    t = LightThread(LightConfig())
    t.start()
    try:
        yield t
    finally:
        t.shutdown()


def _raise(exc):
    def _fn(_light):
        raise exc

    return _fn


def test_exception_in_task_is_delivered_not_hung(worker):
    with pytest.raises(ValueError, match="boom"):
        worker.submit(_raise(ValueError("boom")))
    # worker survived and still serves
    assert worker.submit(lambda _l: 42) == 42


def test_base_exception_in_task_does_not_kill_the_worker(worker):
    with pytest.raises(SystemExit):
        worker.submit(_raise(SystemExit("stop")))
    assert worker.submit(lambda _l: "still here") == "still here"


def test_timeout_raises_instead_of_blocking_forever(worker):
    with pytest.raises(TimeoutError):
        worker.submit(lambda _l: time.sleep(2), timeout=0.05)


def test_submit_after_shutdown_raises(monkeypatch):
    monkeypatch.setattr("light_api.worker.Light", _FakeLightCM)
    t = LightThread(LightConfig())
    t.start()
    t.shutdown()
    with pytest.raises(RuntimeError, match="not running"):
        t.submit(lambda _l: 1)


def test_queued_calls_are_failed_when_the_worker_stops(monkeypatch):
    monkeypatch.setattr("light_api.worker.Light", _FakeLightCM)
    t = LightThread(LightConfig())
    t.start()

    pending: Future = Future()
    t._queue.put((lambda _l: 1, pending))  # simulate an in-flight enqueue
    t._fail_pending()  # worker exit path

    with pytest.raises(RuntimeError, match="stopped"):
        pending.result(timeout=1)
    with pytest.raises(RuntimeError, match="not running"):
        t.submit(lambda _l: 1)


def test_failed_session_setup_surfaces_and_does_not_hang(monkeypatch):
    class _Boom:
        def __init__(self, **_kw):
            raise RuntimeError("login failed")

    monkeypatch.setattr("light_api.worker.Light", _Boom)
    t = LightThread(LightConfig())
    with pytest.raises(RuntimeError, match="login failed"):
        t.start()
    with pytest.raises(RuntimeError, match="not running"):
        t.submit(lambda _l: 1)
