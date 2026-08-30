import functools
import click
import httpx
from .client import Light


def _password_prompt():
    """Hidden-input prompt used by --ask, invoked by login() only when a password
    is actually required (no cached session, nothing in file/env)."""
    return click.prompt("Light account password", hide_input=True)


def with_light(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        obj = click.get_current_context().find_root().obj or {}
        try:
            light = Light(
                email=obj.get("email"),
                email_file=obj.get("email_file"),
                password_prompt=_password_prompt if obj.get("ask_password") else None,
                password_file=obj.get("password_file"),
                phone=obj.get("phone_number"),
                phone_file=obj.get("phone_number_file"),
                device_id=obj.get("device_id"),
                device_id_file=obj.get("device_id_file"),
                cache_enabled=obj.get("cache_enabled", False),
            )
            light.__enter__()
            return f(light, *args, **kwargs)
        except RuntimeError as e:
            raise click.ClickException(str(e))
        except httpx.TimeoutException:
            raise click.ClickException(
                "Request to Light API exceeded 30-second timeout. Please try again."
            )
        except httpx.HTTPError as e:
            raise click.ClickException(f"Request to Light API failed: {e}")

    return wrapper
