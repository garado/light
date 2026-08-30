"""Test that the daemon shuts down cleanly on SIGTERM/SIGINT."""

import json
import queue
import signal
import subprocess
import sys
import threading

import pytest

_HANDSHAKE_TIMEOUT = 10
_EXIT_TIMEOUT = 10


def _read_handshake(proc: subprocess.Popen) -> dict:
    """Read the one handshake line with a bounded wait.

    Fail loudly with the child's stderr + exit status if it never comes.
    """
    result: queue.Queue[str] = queue.Queue(maxsize=1)
    threading.Thread(
        target=lambda: result.put(proc.stdout.readline()), daemon=True
    ).start()

    try:
        line = result.get(timeout=_HANDSHAKE_TIMEOUT)
    except queue.Empty:
        proc.kill()
        raise AssertionError(
            f"daemon printed no handshake within {_HANDSHAKE_TIMEOUT}s "
            f"(still running={proc.poll() is None})\n"
            f"stderr:\n{proc.stderr.read()}"
        )

    if not line:  # EOF - child exited before printing
        raise AssertionError(
            f"daemon exited before handshake (exit={proc.wait(2)})\n"
            f"stderr:\n{proc.stderr.read()}"
        )
    return json.loads(line)


@pytest.mark.parametrize("sig", [signal.SIGTERM, signal.SIGINT])
def test_shuts_down_cleanly_on_signal(sig):
    proc = subprocess.Popen(
        [sys.executable, "-m", "light_daemon", "--fake", "--port", "0"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        handshake = _read_handshake(proc)
        assert {"host", "port", "token"} <= handshake.keys()

        proc.send_signal(sig)
        code = proc.wait(timeout=_EXIT_TIMEOUT)
        assert (
            code == 0
        ), f"expected clean exit, got {code}\nstderr:\n{proc.stderr.read()}"
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=5)
