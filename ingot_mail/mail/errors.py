"""The errors of the mail, :class:`MailError` the base of all."""

__all__ = ("MailDeliveryError", "MailError", "MailHeaderError")

import typing as t


class MailError(Exception):
    """An error of the mail; ``args`` are the message, then its context."""

    @t.override
    def __str__(self) -> str:
        return str(self.args[0])


class MailHeaderError(MailError, ValueError):
    """
    A mail refused before it is sent: a header unfit, empty, or with a
    character not printable, a line break for one, which would inject
    another header.
    """

    args: tuple[str, str]

    @classmethod
    def for_header(cls, name: str) -> t.Self:
        return cls(f"a header unfit to send: {name}", name)

    @property
    def header(self) -> str:
        """
        The name of the header: ``sender``, ``to``, ``subject``, or that of
        a header of the mail as it tells it.
        """
        return self.args[1]


class MailDeliveryError(MailError):
    """
    A mail the server did not take. Transient when sending it again later
    may succeed: no connection, a timeout, a reply of SMTP 4xx; the retry is
    the caller's. A backend raises it from the error of its library.
    """

    args: tuple[str, str, bool]

    @classmethod
    def for_reason(cls, reason: str, *, is_transient: bool) -> t.Self:
        return cls(f"a mail not delivered: {reason}", reason, is_transient)

    @property
    def reason(self) -> str:
        return self.args[1]

    @property
    def is_transient(self) -> bool:
        return self.args[2]
