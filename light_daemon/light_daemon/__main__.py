"""Run the daemon."""

from light_daemon.server import serve
from light_daemon.testing import FakeLight, FakePw


def main() -> None:
    serve(FakePw(FakeLight()))


if __name__ == "__main__":
    main()
