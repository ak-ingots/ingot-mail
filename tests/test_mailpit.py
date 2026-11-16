"""
The mailer of SMTP against Mailpit: run by ``make integration``, which starts
the servers of ``docker-compose.yml`` and sets ``INGOT_MAIL_TEST_MAILPIT``;
skipped without it. The contract runs in the clear and over STARTTLS with a
login, the mail read back by the HTTP API of Mailpit.
"""

import asyncio
import email.header
import json
import os
import ssl
import typing as t
import unittest
import urllib.request
from unittest import mock

from ingot_mail import MailProject
from ingot_mail.contrib.aiosmtplib import AiosmtplibMailer
from ingot_mail.mail import Mail, MailDeliveryError, MailUnit
from ingot_mail.testing.contracts import MailerContract
from ingots.puer import Slot

IS_MAILPIT = bool(os.environ.get("INGOT_MAIL_TEST_MAILPIT"))


class SelfSignedMailer(AiosmtplibMailer):
    """The certificate of Mailpit is its own: not verified."""

    @t.override
    def _get_tls_context(self) -> ssl.SSLContext | None:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context


class MailpitMailUnit(MailUnit):
    mailer = Slot(SelfSignedMailer)


class MailpitProject(MailProject):
    mail = Slot(MailpitMailUnit)


if t.TYPE_CHECKING:
    TestCase: t.TypeAlias = unittest.IsolatedAsyncioTestCase
else:
    TestCase = object


class MailpitMixin(TestCase):
    """A Mailpit emptied, the configs of the mailer for it."""

    smtp_port: str
    http_port: str
    configs: dict[str, str] = {}

    @t.override
    async def asyncSetUp(self) -> None:
        await self.call_api("DELETE", "messages")
        environ = {
            "INGOT_IS_PRINT_CONFIGS": "off",
            "INGOT_MAIL_SMTP_HOST": "127.0.0.1",
            "INGOT_MAIL_SMTP_PORT": self.smtp_port,
            "INGOT_MAIL_SMTP_TIMEOUT": "10",
            **self.configs,
        }
        self.enterContext(mock.patch.dict(os.environ, environ, clear=True))
        # the logging is not under test: keep the handlers of the test run
        self.enterContext(mock.patch("logging.config.dictConfig"))
        await super().asyncSetUp()

    async def create_project(self) -> MailProject:
        project = MailpitProject()
        await project._configure()
        self.addAsyncCleanup(project._do_shut_down)
        return project

    async def get_delivered(self) -> tuple[Mail, ...]:
        listed = await self.call_api("GET", "messages")
        delivered = []
        for item in reversed(listed["messages"]):  # the newest first
            message = await self.call_api("GET", f"message/{item['ID']}")
            headers = await self.call_api("GET", f"message/{item['ID']}/headers")
            delivered.append(
                Mail(
                    to=tuple(to["Address"] for to in message["To"]),
                    subject=message["Subject"],
                    text=message["Text"].replace("\r\n", "\n"),
                    sender=message["From"]["Address"],
                    headers={
                        name: _decode(values[-1]) for name, values in headers.items()
                    },
                )
            )
        return tuple(delivered)

    async def call_api(self, method: str, path: str) -> t.Any:
        url = f"http://127.0.0.1:{self.http_port}/api/v1/{path}"
        request = urllib.request.Request(url, method=method)

        def call() -> t.Any:
            with urllib.request.urlopen(request, timeout=10) as response:
                body = response.read()
            return json.loads(body) if body.startswith(b"{") else None

        return await asyncio.to_thread(call)


@unittest.skipUnless(IS_MAILPIT, "no Mailpit: run make integration")
class MailpitTestCase(MailpitMixin, MailerContract, unittest.IsolatedAsyncioTestCase):
    smtp_port = os.environ.get("INGOT_MAIL_TEST_SMTP_PORT", "11025")
    http_port = os.environ.get("INGOT_MAIL_TEST_HTTP_PORT", "18025")
    configs = {"INGOT_MAIL_SMTP_TLS": "NONE"}


@unittest.skipUnless(IS_MAILPIT, "no Mailpit: run make integration")
class MailpitTlsTestCase(
    MailpitMixin, MailerContract, unittest.IsolatedAsyncioTestCase
):
    smtp_port = os.environ.get("INGOT_MAIL_TEST_TLS_SMTP_PORT", "11026")
    http_port = os.environ.get("INGOT_MAIL_TEST_TLS_HTTP_PORT", "18026")
    configs = {
        "INGOT_MAIL_SMTP_TLS": "STARTTLS",
        "INGOT_MAIL_SMTP_USER": "ingot",
        "INGOT_MAIL_SMTP_PASSWORD": "p@ss:w/rd",
    }

    async def test_a_wrong_password_is_not_transient(self) -> None:
        os.environ["INGOT_MAIL_SMTP_PASSWORD"] = "wrong"
        project = await self.create_project()
        with self.assertRaises(MailDeliveryError) as caught:
            await project.mail.mailer.send(Mail(to=("al@b.c",), subject="Hi", text=""))
        self.assertFalse(caught.exception.is_transient)

    async def test_the_clear_is_refused(self) -> None:
        os.environ["INGOT_MAIL_SMTP_TLS"] = "NONE"
        project = await self.create_project()
        with self.assertRaises(MailDeliveryError) as caught:
            await project.mail.mailer.send(Mail(to=("al@b.c",), subject="Hi", text=""))
        self.assertFalse(caught.exception.is_transient)


def _decode(value: str) -> str:
    """A header as Mailpit tells it, its words of RFC 2047 decoded."""
    return str(email.header.make_header(email.header.decode_header(value)))
