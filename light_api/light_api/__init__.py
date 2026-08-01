import functools
import click
from .client import Light


def with_light(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
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
            )
            light.__enter__()
            return f(light, *args, **kwargs)
        except RuntimeError as e:
            raise click.ClickException(str(e))

    return wrapper
