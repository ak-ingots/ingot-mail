import contextlib
import io
import os
import typing as t
import unittest
from unittest import mock

import ingot_mail
from ingot_mail.__main__ import main
from ingot_mail.logging import MailLoggingUnit
from ingot_mail.mail import MailUnit
from ingot_mail.settings import MailSettingsUnit
from ingot_mail.settings.configs import MailConfigs
from ingots.defaults import Project
from ingots.puer.cli import CommandRunner


class ProjectTestCase(unittest.TestCase):
    @t.override
    def setUp(self) -> None:
        self.enterContext(mock.patch.dict(os.environ, clear=True))
        # the logging is not under test: keep the handlers of the test run
        self.enterContext(mock.patch("logging.config.dictConfig"))

    def run_project(self, *argv: str) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = CommandRunner(
                ingot_mail.MailProject,
                ["--config", "IS_PRINT_CONFIGS=off", *argv],
            ).run()
        return code, out.getvalue()

    def test_the_project_extends_the_defaults(self) -> None:
        self.assertTrue(issubclass(ingot_mail.MailProject, Project))
        self.assertIs(ingot_mail.MailProject.settings.cls, MailSettingsUnit)
        self.assertIs(ingot_mail.MailProject.logging.cls, MailLoggingUnit)
        self.assertIs(MailSettingsUnit.configs.cls, MailConfigs)
        self.assertIs(ingot_mail.MailProject.mail.cls, MailUnit)

    def test_the_configs_of_the_addon_are_read(self) -> None:
        os.environ["INGOT_MAIL_LOGGING_LEVEL"] = "debug"
        code, out = self.run_project("settings", "list")
        self.assertEqual(code, 0)
        self.assertIn("MAIL_LOGGING_LEVEL = DEBUG\n", out)
        self.assertIn("MAIL_FROM = noreply@localhost\n", out)

    def test_the_logging_has_the_logger_of_the_addon(self) -> None:
        code, out = self.run_project(
            "--config", "MAIL_LOGGING_LEVEL=warning", "logging", "info"
        )
        self.assertEqual(code, 0)
        self.assertIn("        ingot_mail:\n            level: 30\n", out)

    def test_the_addon_runs_on_its_own(self) -> None:
        os.environ["INGOT_IS_PRINT_CONFIGS"] = "off"
        with (
            mock.patch("sys.argv", ["ingot_mail", "logging", "info"]),
            contextlib.redirect_stdout(io.StringIO()) as out,
            self.assertRaises(SystemExit) as exit,
        ):
            main()
        self.assertEqual(exit.exception.code, 0)
        self.assertIn("ingot_mail:", out.getvalue())
