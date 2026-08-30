"""Run the daemon: `python -m light_daemon` / `light-daemon`."""

from __future__ import annotations

import argparse
import sys

from light_api.worker import LightConfig, LightThread

from light_daemon.auth import generate_token
from light_daemon.server import serve


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="light-daemon",
        description="Local gRPC daemon for the Light Phone API (loopback only).",
        allow_abbrev=False,
    )
    p.add_argument(
        "--port",
        type=int,
        default=0,
        help="TCP port on 127.0.0.1 (0 = OS-assigned, printed on start).",
    )
    p.add_argument("--email")
    p.add_argument("--email-file")
    p.add_argument("--password-file")
    p.add_argument("--phone-number")
    p.add_argument("--phone-number-file")
    p.add_argument("--device-id")
    p.add_argument("--device-id-file")
    p.add_argument(
        "--cache", action="store_true", help="Enable local response caching."
    )
    p.add_argument(
        "--fake",
        action="store_true",
        help="Serve an in-memory fake session; no credentials needed (dev only).",
    )
    return p


def config_from_args(args: argparse.Namespace) -> LightConfig:
    return LightConfig(
        email=args.email,
        email_file=args.email_file,
        password_file=args.password_file,
        phone=args.phone_number,
        phone_file=args.phone_number_file,
        device_id=args.device_id,
        device_id_file=args.device_id_file,
        cache_enabled=args.cache,
    )


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    token = generate_token()

    if args.fake:
        from light_daemon.testing import FakeLight, FakePw

        serve(FakePw(FakeLight()), port=args.port, token=token)
        return

    worker = LightThread(config_from_args(args))
    try:
        worker.start()
    except Exception as e:  # bad credentials, network, multi-device ambiguity, ...
        print(f"light-daemon: could not start Light session: {e}", file=sys.stderr)
        raise SystemExit(1)

    serve(worker, port=args.port, token=token)


if __name__ == "__main__":
    main()
