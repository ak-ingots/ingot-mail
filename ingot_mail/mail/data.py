"""The data of the mail."""

__all__ = ("Mail",)

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True, kw_only=True)
class Mail:
    """
    A mail of plain text. Its addresses and its text stay out of the
    ``repr``, as the text may hold a code. With no ``sender``, the mailer
    gives its own, ``MAIL_FROM``. ``headers`` are those of the application,
    ``X-Request-ID`` for one, its own; those of the mailer it may not set.
    """

    to: tuple[str, ...] = field(repr=False)
    subject: str
    text: str = field(repr=False)
    sender: str | None = field(default=None, repr=False)
    headers: Mapping[str, str] = field(default_factory=dict, repr=False, hash=False)
