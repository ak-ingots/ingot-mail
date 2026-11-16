"""Runs the addon on its own: ``python -m ingot_mail logging info``."""

import sys

from ingots.defaults.logging import configure_startup_logging
from ingots.puer.cli import CommandRunner

from .project import MailProject


def main() -> None:
    configure_startup_logging()
    sys.exit(CommandRunner(MailProject).run())


if __name__ == "__main__":
    main()
