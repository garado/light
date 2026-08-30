"""Argument parsing/config mapping for the daemon entrypoint.

The `serve()` and real `LightThread` paths aren't exercised here since they block and need credentials.
"""

import pytest

from light_daemon.__main__ import build_arg_parser, config_from_args


def test_config_from_args_maps_every_flag():
    args = build_arg_parser().parse_args(
        [
            "--email",
            "a@b.c",
            "--email-file",
            "/e",
            "--password-file",
            "/pw",
            "--phone-number",
            "5551234567",
            "--phone-number-file",
            "/pn",
            "--device-id",
            "dev-1",
            "--device-id-file",
            "/di",
            "--cache",
        ]
    )
    cfg = config_from_args(args)

    assert cfg.email == "a@b.c"
    assert cfg.email_file == "/e"
    assert cfg.password_file == "/pw"
    assert cfg.phone == "5551234567"  # --phone-number -> LightConfig.phone
    assert cfg.phone_file == "/pn"
    assert cfg.device_id == "dev-1"
    assert cfg.device_id_file == "/di"
    assert cfg.cache_enabled is True


def test_defaults_are_all_unset():
    args = build_arg_parser().parse_args([])
    cfg = config_from_args(args)

    assert (cfg.email, cfg.email_file, cfg.password_file) == (None, None, None)
    assert (cfg.phone, cfg.phone_file) == (None, None)
    assert (cfg.device_id, cfg.device_id_file) == (None, None)
    assert cfg.cache_enabled is False
    assert args.port == 0
    assert args.fake is False


def test_no_password_flag():
    # the daemon never takes a plaintext password on the command line
    with pytest.raises(SystemExit):
        build_arg_parser().parse_args(["--password", "hunter2"])
