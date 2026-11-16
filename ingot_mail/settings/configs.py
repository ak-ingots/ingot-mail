"""The configs of the addon, named ``MAIL_*``."""

__all__ = ("MailConfigs",)

import logging

from ingots.defaults.settings.configs import Configs, LogLevelConfig, StrConfig


class MailConfigs(Configs):
    """The configs of the defaults with those of the mail."""

    MAIL_LOGGING_LEVEL = LogLevelConfig(logging.INFO)
    MAIL_FROM = StrConfig("noreply@localhost")  # the sender of a mail telling none
