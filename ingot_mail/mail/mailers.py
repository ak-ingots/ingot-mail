"""
The mailer: the interface a backend in ``ingot_mail.contrib`` implements,
which delivers a mail.
"""

__all__ = ("BaseMailer",)

import abc
import typing as t

from ingots.puer import Entity

from .data import Mail
from .errors import MailHeaderError

if t.TYPE_CHECKING:
    from ingot_mail.project import MailProject

# The headers a mailer sets, or that tell where a mail goes: a mail may not
# set them by its own headers, in any case of the letters.
RESERVED_HEADERS: t.Final = frozenset(
    {
        "bcc",
        "cc",
        "content-transfer-encoding",
        "content-type",
        "date",
        "from",
        "message-id",
        "mime-version",
        "sender",
        "subject",
        "to",
    }
)
HEADER_NAME_LETTERS: t.Final = frozenset(map(chr, range(33, 127))) - {":"}


class BaseMailer(Entity):
    """
    The mailer, the slot ``mailer`` of the mail, abstract: what a backend
    implements. A mail unfit to send is refused before the backend sees it.
    """

    project: "MailProject"

    @t.final
    async def send(self, mail: Mail) -> None:
        """
        Delivers a mail from its sender, or from that of the mailer.

        :raises MailHeaderError: no sender or no address, or a character
            not printable, a line break for one, in the sender, an address,
            the subject or a header of the mail; a header of the mailer, or
            a name of a header not of printable ASCII.
        :raises MailDeliveryError: the server did not take it.
        """
        sender = self._get_sender(mail)
        if not sender or not sender.isprintable():
            raise MailHeaderError.for_header("sender")
        if not mail.to or not all(to and to.isprintable() for to in mail.to):
            raise MailHeaderError.for_header("to")
        if not mail.subject.isprintable():
            raise MailHeaderError.for_header("subject")
        for name, value in mail.headers.items():
            if (
                not name
                or not HEADER_NAME_LETTERS.issuperset(name)
                or name.lower() in RESERVED_HEADERS
                or not value.isprintable()
            ):
                raise MailHeaderError.for_header(name)
        await self._send(mail, sender)

    def _get_sender(self, mail: Mail) -> str:
        """The address the mail is from: its own, else ``MAIL_FROM``."""
        if mail.sender is not None:
            return mail.sender
        return self.project.settings.configs.MAIL_FROM

    @abc.abstractmethod
    async def _send(self, mail: Mail, sender: str) -> None:
        """Delivers the mail, checked, from the sender."""
        raise NotImplementedError(f"{type(self).__qualname__}._send")
