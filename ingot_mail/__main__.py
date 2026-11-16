"""
Runs the addon on its own: ``python -m ingot_mail logging info``. The mailer
is in memory, so no mail goes out.
"""

import sys

from ingots.defaults.logging import configure_startup_logging
from ingots.puer import Slot
from ingots.puer.cli import CommandRunner

from .contrib.memory import MemoryMailer
from .mail import MailUnit
from .project import MailProject


class MailMemoryUnit(MailUnit):
    mailer = Slot(MemoryMailer)


class MailMemoryProject(MailProject):
    mail = Slot(MailMemoryUnit)


def main() -> None:
    configure_startup_logging()
    sys.exit(CommandRunner(MailMemoryProject).run())


if __name__ == "__main__":
    main()
