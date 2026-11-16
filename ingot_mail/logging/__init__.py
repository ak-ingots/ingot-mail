"""The logging unit of the defaults with the logger of the addon."""

__all__ = ("MailLoggingUnit",)

import typing as t

from ingots.defaults.logging import LoggingUnit

if t.TYPE_CHECKING:
    from ..project import MailProject


class MailLoggingUnit(LoggingUnit):
    """
    The logging unit, with the logger of the addon, ``ingot_mail``, at
    ``MAIL_LOGGING_LEVEL``.
    """

    project: "MailProject"

    @t.override
    def build_loggers(self) -> dict[str, dict[str, t.Any]]:
        level = self.project.settings.configs.MAIL_LOGGING_LEVEL
        addon = {"level": level, "handlers": ["default"], "propagate": False}
        return {**super().build_loggers(), "ingot_mail": addon}
