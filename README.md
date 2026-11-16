# ingot-mail

[![ci](https://github.com/ak-ingots/ingot-mail/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ak-ingots/ingot-mail/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/ak-ingots/ingot-mail/blob/main/LICENSE)

<!-- Links must be absolute: this README also renders on PyPI. -->

The mail of Ingots applications. An addon of
[Ingots](https://github.com/ak-ingots/ingots).

**Status:** pre-alpha: the mail and its mailer, the interface of a backend
with its contract, and the mailer in memory; next, the mailer of SMTP on
aiosmtplib.

## For Consumers

### Install

```sh
uv add ingot-mail
```

### Integrate

An application of Ingots has its own configs, settings, logging and project;
each takes the class of the addon among its bases:

```python
# app/project.py
import typing as t

from ingot_mail import MailProject
from ingot_mail.contrib.memory import MemoryMailer
from ingot_mail.logging import MailLoggingUnit
from ingot_mail.mail import MailUnit
from ingot_mail.settings import MailSettingsUnit
from ingot_mail.settings.configs import MailConfigs
from ingots.puer import Slot


class AppConfigs(MailConfigs):
    pass


class AppSettingsUnit(MailSettingsUnit):
    configs = Slot(AppConfigs)


class AppLoggingUnit(MailLoggingUnit):
    project: "AppProject"


class AppMailUnit(MailUnit):
    mailer = Slot(MemoryMailer)


class AppProject(MailProject):
    env_configs_prefix = "APP"
    settings = Slot(AppSettingsUnit)
    logging = Slot(AppLoggingUnit)
    mail = Slot(AppMailUnit)
```

The slot `mailer` of `MailUnit` is abstract: the application declares a
backend. `MemoryMailer` delivers nothing and keeps the mail for the tests,
`get_sent()`.

With other addons, their classes join the same bases:
`class AppConfigs(MailConfigs, MongoDbConfigs)`, and so on, as the
[addon guide](https://github.com/ak-ingots/ingots/blob/main/docs/defaults/addon.md)
of Ingots shows. An application with this addon alone may inherit
`MailProject` and nothing more.

The application runs through its own `__main__.py`:

```python
# app/__main__.py
import sys

from ingots.defaults.logging import configure_startup_logging
from ingots.puer.cli import CommandRunner

from .project import AppProject

configure_startup_logging()
sys.exit(CommandRunner(AppProject).run())
```

```sh
uv run python -m app settings list    # the configs, MAIL_* among them
uv run python -m app logging info     # the loggers, ingot_mail among them
```

### Send

```python
from ingot_mail.mail import Mail

mail = Mail(to=("al@b.c",), subject="Welcome", text="Hello, Al!\n")
await self.project.mail.mailer.send(mail)
```

A mail is from its `sender`, or from `MAIL_FROM` when it tells none. A
header unfit to send, an empty one, or one with a line break, which would
inject another header, is refused before the backend by `MailHeaderError`;
a mail the server did not take is `MailDeliveryError`, `is_transient` when
sending it again later may succeed. The retry is the caller's.

### Test a backend

A backend runs the contract of the mailer, `MailerContract` of
`ingot_mail.testing.contracts`, telling the project and where its mail is
read back:

```python
class AppMailerTestCase(MailerContract, unittest.IsolatedAsyncioTestCase):
    async def create_project(self) -> MailProject:
        return AppProject()

    async def get_delivered(self) -> tuple[Mail, ...]:
        ...
```

### Configs

Set as environment variables with the prefix of the project
(`APP_MAIL_LOGGING_LEVEL`), in a `--configs-file` or with `--config`.

| Name | Default | Meaning |
|---|---|---|
| `MAIL_LOGGING_LEVEL` | `INFO` | the level of the logger of the addon, `ingot_mail` |
| `MAIL_FROM` | `noreply@localhost` | the sender of a mail telling none |

## Development

Requires [uv](https://docs.astral.sh/uv/) and `make`; uv fetches the
interpreters it needs.

```sh
make                 # the target list
make check           # everything CI runs: lint, test, coverage, wheel-test, cl-check
make format          # black
make all             # build the sdist and the wheel into dist/
```

- Every change users should know about adds a news fragment to `changelog.d/`
  (see [its README](https://github.com/ak-ingots/ingot-mail/blob/main/changelog.d/README.md)).
- A release is a pull request setting the version (`uv version X.Y.Z`) and
  collating the changelog (`make cl-build VERSION=X.Y.Z`), then the tag
  `vX.Y.Z` on `main`: the `release` workflow publishes the tested build to
  TestPyPI, tests it as installed from there, then
  publishes it to PyPI. Run by hand, it rehearses on TestPyPI only.
