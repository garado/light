import functools
import click
import httpx
from .client import Light

# prototype hook for `light shell` - when set, with_light() reuses this already-
# authenticated instance instead of constructing+authenticating a new one per
# command
_shared_light: Light | None = None


def set_shared_light(light: Light | None) -> None:
    global _shared_light
    _shared_light = light


def with_light(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if _shared_light is not None:
            return f(_shared_light, *args, **kwargs)

        obj = click.get_current_context().find_root().obj or {}
        try:
            light = Light(
                email=obj.get("email"),
                email_file=obj.get("email_file"),
                password=obj.get("password"),
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
