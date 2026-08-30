"""Test daemon shutdown behavior."""

import json
import signal
import subprocess
import sys

import pytest


@pytest.mark.parametrize("sig", [signal.SIGTERM, signal.SIGINT])
def test_shuts_down_cleanly_on_signal(sig):
    proc = subprocess.Popen(
        [sys.executable, "-m", "light_daemon", "--fake", "--port", "0"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    try:
        handshake = json.loads(proc.stdout.readline())
        assert {"host", "port", "token"} <= handshake.keys()

        proc.send_signal(sig)
        assert (
            proc.wait(timeout=10) == 0
        )  # our handler ran; not killed by default action
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=5)
