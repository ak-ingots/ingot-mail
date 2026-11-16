"""The mailer of SMTP on aiosmtplib, against the server of SMTP of the tests."""

import os
import typing as t
import unittest
from unittest import mock

from ingot_mail import MailProject
from ingot_mail.contrib.aiosmtplib import AiosmtplibMailer
from ingot_mail.mail import Mail, MailDeliveryError, MailUnit
from ingot_mail.testing.contracts import MailerContract
from ingots.puer import Slot

from .smtp import SmtpServer

MAIL: t.Final = Mail(to=("al@b.c", "bo@b.c"), subject="Hi", text="Hello!\n")


class AiosmtplibMailUnit(MailUnit):
    mailer = Slot(AiosmtplibMailer)


class AiosmtplibProject(MailProject):
    mail = Slot(AiosmtplibMailUnit)


if t.TYPE_CHECKING:
    TestCase: t.TypeAlias = unittest.IsolatedAsyncioTestCase
else:
    TestCase = object


class SmtpMixin(TestCase):
    """The server of the tests and the configs of the mailer for it."""

    server: SmtpServer
    configs: dict[str, str] = {}

    @t.override
    async def asyncSetUp(self) -> None:
        self.server = getattr(self, "server", None) or SmtpServer()
        smtp = await self.server.start()
        self.addAsyncCleanup(smtp.wait_closed)
        self.addCleanup(smtp.close)
        environ = {
            "INGOT_IS_PRINT_CONFIGS": "off",
            "INGOT_MAIL_SMTP_HOST": "127.0.0.1",
            "INGOT_MAIL_SMTP_PORT": str(self.server.port),
            "INGOT_MAIL_SMTP_TLS": "NONE",
            "INGOT_MAIL_SMTP_TIMEOUT": "1",
            **self.configs,
        }
        self.enterContext(mock.patch.dict(os.environ, environ, clear=True))
        # the logging is not under test: keep the handlers of the test run
        self.enterContext(mock.patch("logging.config.dictConfig"))
        await super().asyncSetUp()  # a contract creates its project now

    async def create_project(self) -> MailProject:
        project = AiosmtplibProject()
        await project._configure()
        self.addAsyncCleanup(project._do_shut_down)
        return project


class BaseSmtpTestCase(SmtpMixin, unittest.IsolatedAsyncioTestCase):
    pass


class AiosmtplibMailerTestCase(
    SmtpMixin, MailerContract, unittest.IsolatedAsyncioTestCase
):
    @t.override
    async def get_delivered(self) -> tuple[Mail, ...]:
        return self.server.get_delivered()


class AiosmtplibFailuresTestCase(BaseSmtpTestCase):
    async def send(self, **replies: str) -> MailDeliveryError:
        self.server.replies.update(replies)
        project = await self.create_project()
        with self.assertRaises(MailDeliveryError) as caught:
            await project.mail.mailer.send(MAIL)
        self.assertEqual(self.server.messages, [])
        return caught.exception

    async def test_a_reply_4xx_is_transient(self) -> None:
        error = await self.send(DATA="451 try later")
        self.assertTrue(error.is_transient)
        self.assertEqual(error.reason, "451 try later")

    async def test_a_reply_5xx_is_not(self) -> None:
        error = await self.send(MAIL="550 no such sender")
        self.assertFalse(error.is_transient)

    async def test_every_address_refused_for_now_is_transient(self) -> None:
        error = await self.send(RCPT="450 mailbox busy")
        self.assertTrue(error.is_transient)
        self.assertEqual(error.reason, "every address refused")

    async def test_every_address_refused_one_for_good_is_not(self) -> None:
        error = await self.send(**{"RCPT al@b.c": "450 busy", "RCPT bo@b.c": "550 no"})
        self.assertFalse(error.is_transient)

    async def test_a_server_refusing_at_the_greeting_for_now_is_transient(
        self,
    ) -> None:
        error = await self.send(CONNECT="421 too busy")
        self.assertTrue(error.is_transient)

    async def test_no_starttls_where_required_is_not_transient(self) -> None:
        os.environ["INGOT_MAIL_SMTP_TLS"] = "STARTTLS"
        error = await self.send()
        self.assertFalse(error.is_transient)

    async def test_no_server_is_transient(self) -> None:
        os.environ["INGOT_MAIL_SMTP_PORT"] = "1"
        error = await self.send()
        self.assertTrue(error.is_transient)

    async def test_a_silent_server_is_transient(self) -> None:
        self.server.is_silent = True
        error = await self.send()
        self.assertTrue(error.is_transient)


class AiosmtplibMailerLogTestCase(BaseSmtpTestCase):
    async def test_a_mail_sent_is_logged_by_its_id_alone(self) -> None:
        project = await self.create_project()
        with self.assertLogs("ingot_mail", "INFO") as logs:
            await project.mail.mailer.send(MAIL)
        [line] = logs.output
        self.assertRegex(line, r"^INFO:.*:sent the mail <[^>]+@localhost>$")

    async def test_some_addresses_refused_are_a_warning(self) -> None:
        self.server.replies["RCPT bo@b.c"] = "550 no such user"
        project = await self.create_project()
        with self.assertLogs("ingot_mail", "WARNING") as logs:
            await project.mail.mailer.send(MAIL)
        self.assertIn("1 of its addresses refused", logs.output[0])
        self.assertNotIn("bo@b.c", logs.output[0])
        self.assertEqual(len(self.server.messages), 1)


class AiosmtplibMailerLoginTestCase(BaseSmtpTestCase):
    configs = {"INGOT_MAIL_SMTP_USER": "ingot", "INGOT_MAIL_SMTP_PASSWORD": "p@ss"}

    @t.override
    async def asyncSetUp(self) -> None:
        self.server = SmtpServer(is_auth=True)
        await super().asyncSetUp()

    async def test_it_logs_in_by_the_configs(self) -> None:
        project = await self.create_project()
        await project.mail.mailer.send(MAIL)
        self.assertEqual(self.server.logins, ["\0ingot\0p@ss"])
        self.assertEqual(len(self.server.messages), 1)
