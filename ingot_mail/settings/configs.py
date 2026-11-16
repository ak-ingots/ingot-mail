"""The configs of the addon, named ``MAIL_*``."""

__all__ = ("MailConfigs", "MailSmtpTls")

import enum
import logging

from ingots.defaults.settings.configs import (
    Configs,
    EnumConfig,
    FloatConfig,
    IntConfig,
    LogLevelConfig,
    SecureStrConfig,
    StrConfig,
)


class MailSmtpTls(enum.Enum):
    """How a connection to a server of SMTP is secured."""

    NONE = enum.auto()  # in the clear: a server of the tests alone
    STARTTLS = enum.auto()  # upgraded after the greeting, the port 587
    TLS = enum.auto()  # from the start, the port 465


class MailConfigs(Configs):
    """
    The configs of the defaults with those of the mail: the sender, and the
    server of SMTP of the backends sending by it, ``MAIL_SMTP_*``.
    """

    MAIL_LOGGING_LEVEL = LogLevelConfig(logging.INFO)
    MAIL_FROM = StrConfig("noreply@localhost")  # the sender of a mail telling none
    MAIL_SMTP_HOST = StrConfig("localhost")
    MAIL_SMTP_PORT = IntConfig(587)
    MAIL_SMTP_USER = StrConfig("")  # empty: no authentication
    MAIL_SMTP_PASSWORD = SecureStrConfig("")
    MAIL_SMTP_TLS = EnumConfig(MailSmtpTls.STARTTLS)
    MAIL_SMTP_TIMEOUT = FloatConfig(30.0)  # seconds
