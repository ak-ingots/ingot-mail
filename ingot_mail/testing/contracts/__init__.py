"""
The contracts of the addon (ADRs 0005, 0010 of the ecosystem): the guarantees of its
public API, as tests a consumer runs on its own classes. Nothing imports them at
runtime. A test case takes a contract and tells what to run it on::

    class AppMailerTestCase(MailerContract, unittest.IsolatedAsyncioTestCase):
        async def create_project(self) -> MailProject:
            ...

        async def get_delivered(self) -> tuple[Mail, ...]:
            ...
"""

__all__ = ("BaseMailContract", "MailerContract")

from .base import BaseMailContract
from .mailer import MailerContract
