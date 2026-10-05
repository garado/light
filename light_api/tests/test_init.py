"""Tests for light_api.with_light's exception translation and Light wiring."""

import click
import httpx
import pytest
from unittest.mock import MagicMock, patch

from light_api import with_light


def _run(f, obj=None):
    """Invoke f (already decorated with @with_light) inside a click context."""
    ctx = click.Context(click.Command("test"), obj=obj or {})
    with ctx:
        return f()


@pytest.fixture(autouse=True)
def mock_light():
    with patch("light_api.Light") as mock_cls:
        instance = MagicMock()
        instance.__enter__.return_value = instance
        mock_cls.return_value = instance
        yield mock_cls


class TestWithLightHappyPath:
    def test_passes_light_instance_to_wrapped_function(self, mock_light):
        @with_light
        def cmd(light):
            return light

        result = _run(cmd)
        assert result is mock_light.return_value.__enter__.return_value

    def test_builds_light_from_context_obj(self, mock_light):
        @with_light
        def cmd(light):
            return light

        _run(cmd, obj={"email": "a@b.com", "device_id": "dev-1", "cache_enabled": True})

        mock_light.assert_called_once_with(
            email="a@b.com",
            email_file=None,
            password_prompt=None,
            password_file=None,
            phone=None,
            phone_file=None,
            device_id="dev-1",
            device_id_file=None,
            cache_enabled=True,
        )

    def test_forwards_extra_args_and_kwargs(self, mock_light):
        @with_light
        def cmd(light, a, b=None):
            return (a, b)

        assert _run(lambda: cmd("x", b="y")) == ("x", "y")


class TestWithLightExceptionTranslation:
    def test_runtime_error_becomes_click_exception(self, mock_light):
        @with_light
        def cmd(light):
            raise RuntimeError("boom")

        with pytest.raises(click.ClickException, match="boom"):
            _run(cmd)

    def test_timeout_becomes_click_exception_with_fixed_message(self, mock_light):
        @with_light
        def cmd(light):
            raise httpx.TimeoutException("too slow")

        with pytest.raises(click.ClickException, match="exceeded 30-second timeout"):
            _run(cmd)

    def test_http_error_becomes_click_exception_with_detail(self, mock_light):
        @with_light
        def cmd(light):
            raise httpx.HTTPError("connection reset")

        with pytest.raises(
            click.ClickException, match="Request to Light API failed: connection reset"
        ):
            _run(cmd)
