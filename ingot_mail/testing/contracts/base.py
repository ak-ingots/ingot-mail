"""The base of the contracts: a project to run on."""

__all__ = ("BaseMailContract",)

import abc
import typing as t
import unittest

if t.TYPE_CHECKING:
    from ingot_mail.project import MailProject

    TestCase: t.TypeAlias = unittest.IsolatedAsyncioTestCase
else:
    TestCase = abc.ABC


class BaseMailContract(TestCase):
    """A contract: a subclass tells what it checks, a test case on what."""

    @abc.abstractmethod
    async def create_project(self) -> "MailProject":
        """
        The project to run on, its mailer having sent nothing. The test case
        cleans up what it needs to, with ``addAsyncCleanup()``.
        """
        raise NotImplementedError(f"{type(self).__qualname__}.create_project")

    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.project = await self.create_project()
