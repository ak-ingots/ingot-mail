"""
The mailer in memory: for the tests and the addon run on its own,
delivering nothing. An application declares it in the slot of its mail:
``mailer = Slot(MemoryMailer)``.
"""

__all__ = ("MemoryMailer",)

import dataclasses
import typing as t

from ingot_mail.mail import BaseMailer, Mail


class MemoryMailer(BaseMailer):
    """The mail is kept, in the order it is sent, for the tests to read."""

    def __init__(self) -> None:
        super().__init__()
        self._sent: list[Mail] = []

    @t.final
    def get_sent(self) -> tuple[Mail, ...]:
        """The mail sent so far, in its order, each with the sender it was sent from."""
        return tuple(self._sent)

    @t.override
    async def _send(self, mail: Mail, sender: str) -> None:
        self._sent.append(dataclasses.replace(mail, sender=sender))
