"""The contracts of the addon, on the mailer in memory."""

import typing as t
import unittest

from ingot_mail.__main__ import MailMemoryProject
from ingot_mail.mail import Mail
from ingot_mail.testing.contracts import MailerContract


class MemoryMailerTestCase(MailerContract, unittest.IsolatedAsyncioTestCase):
    project: MailMemoryProject

    @t.override
    async def create_project(self) -> MailMemoryProject:
        return MailMemoryProject()

    @t.override
    async def get_delivered(self) -> tuple[Mail, ...]:
        return self.project.mail.mailer.get_sent()
