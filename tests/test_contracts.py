"""The contracts of the addon, on the mailer in memory."""

import typing as t
import unittest

from ingot_mail.__main__ import MailMemoryProject
from ingot_mail.contrib.memory import MemoryMailer
from ingot_mail.mail import Mail
from ingot_mail.project import MailProject
from ingot_mail.testing.contracts import MailerContract


class MemoryMailerTestCase(MailerContract, unittest.IsolatedAsyncioTestCase):
    @t.override
    async def create_project(self) -> MailProject:
        return MailMemoryProject()

    @t.override
    async def get_delivered(self) -> tuple[Mail, ...]:
        return t.cast(MemoryMailer, self.project.mail.mailer).get_sent()
