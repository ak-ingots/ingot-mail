"""
The contract of a mailer: what a backend guarantees, whatever it delivers
by. A test case tells where the mail it delivered is read back, a server of
SMTP catching it for one.
"""

__all__ = ("MailerContract",)

import abc
import dataclasses
import typing as t

from ingot_mail.mail import Mail, MailHeaderError

from .base import BaseMailContract

CODE: t.Final = Mail(to=("al@b.c",), subject="Your code", text="Your code is 123456.\n")


class MailerContract(BaseMailContract):
    """
    The mailer of the mail of a project: a mail sent is delivered as it was
    sent, its addresses, its subject, its text, from its sender or from
    ``MAIL_FROM``; a mail unfit to send is not delivered.
    """

    @abc.abstractmethod
    async def get_delivered(self) -> tuple[Mail, ...]:
        """
        The mail the mailer of the project delivered so far, each with the
        sender it came from.
        """
        raise NotImplementedError(f"{type(self).__qualname__}.get_delivered")

    async def test_a_mail_is_delivered_as_sent_from_the_default_sender(
        self,
    ) -> None:
        await self.project.mail.mailer.send(CODE)
        self.assertEqual(await self.get_delivered(), (self._from_default(CODE),))

    async def test_a_mail_is_delivered_from_its_own_sender(self) -> None:
        mail = dataclasses.replace(CODE, sender="help@b.c")
        await self.project.mail.mailer.send(mail)
        self.assertEqual(await self.get_delivered(), (mail,))

    async def test_a_mail_of_any_letters_is_delivered_intact(self) -> None:
        mail = Mail(to=("al@b.c",), subject="Ваш код", text="Код: 123456 — ✓\n")
        await self.project.mail.mailer.send(mail)
        self.assertEqual(await self.get_delivered(), (self._from_default(mail),))

    async def test_a_mail_to_several_addresses_is_delivered_to_each(self) -> None:
        mail = dataclasses.replace(CODE, to=("al@b.c", "bo@b.c", "cy@b.c"))
        await self.project.mail.mailer.send(mail)
        self.assertEqual(await self.get_delivered(), (self._from_default(mail),))

    async def test_every_mail_is_delivered(self) -> None:
        mails = [
            Mail(to=(f"{name}@b.c",), subject="Your code", text=f"{name}\n")
            for name in ("al", "bo", "cy")
        ]
        for mail in mails:
            await self.project.mail.mailer.send(mail)
        delivered = await self.get_delivered()
        expected = [self._from_default(mail) for mail in mails]
        self.assertEqual(sorted(delivered, key=lambda mail: mail.to), expected)

    async def test_a_mail_unfit_to_send_is_not_delivered(self) -> None:
        injected = "Hi\r\nBcc: all@b.c"
        for header, mail in (
            ("to", dataclasses.replace(CODE, to=())),
            ("to", dataclasses.replace(CODE, to=("",))),
            ("to", dataclasses.replace(CODE, to=("al@b.c\nBcc: all@b.c",))),
            ("subject", dataclasses.replace(CODE, subject=injected)),
            ("sender", dataclasses.replace(CODE, sender="")),
            ("sender", dataclasses.replace(CODE, sender="a@b.c\nBcc: all@b.c")),
        ):
            with self.subTest(mail=mail), self.assertRaises(MailHeaderError) as caught:
                await self.project.mail.mailer.send(mail)
            self.assertEqual(caught.exception.header, header)
        self.assertEqual(await self.get_delivered(), ())

    def _from_default(self, mail: Mail) -> Mail:
        """The mail as delivered with no sender of its own."""
        sender = self.project.settings.configs.MAIL_FROM
        return dataclasses.replace(mail, sender=sender)
