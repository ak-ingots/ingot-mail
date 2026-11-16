# ingot-mail Changelog

<!-- towncrier release notes start -->

## [0.2.0] - 2026-11-16
### Added
- The mail and its mailer: `Mail`, a mail of plain text, its addresses and its
  text out of the `repr`; `BaseMailer`, the slot `mailer` of `MailUnit`,
  abstract, whose `send()` refuses a header unfit to send by `MailHeaderError`
  before the backend, the sender that of the mail or `MAIL_FROM`; a mail not
  delivered is `MailDeliveryError`, transient or not. `MemoryMailer` of
  `ingot_mail.contrib.memory` keeps the mail for the tests, and
  `python -m ingot_mail` runs with it; `MailerContract` of
  `ingot_mail.testing.contracts` is what a backend guarantees.
- The mailer of SMTP, `AiosmtplibMailer` of `ingot_mail.contrib.aiosmtplib`,
  with the extra `aiosmtplib`: a connection a mail, configured by
  `MAIL_SMTP_HOST`, `MAIL_SMTP_PORT`, `MAIL_SMTP_USER`, `MAIL_SMTP_PASSWORD`,
  `MAIL_SMTP_TLS` (`STARTTLS` by default, `TLS` or `NONE`) and
  `MAIL_SMTP_TIMEOUT`, read by hooks a subclass overrides. A failure is
  `MailDeliveryError`, transient for no connection, a timeout or a reply 4xx.
  The logger `ingot_mail` tells each mail sent by its message id alone.
- The headers of a mail, `Mail.headers`, the application's own,
  `X-Request-ID` for one: `send()` refuses a name not of printable ASCII or
  with a colon, a value with a character not printable, and a header the
  mailer sets or that tells where the mail goes, `From`, `To`, `Cc`, `Bcc`,
  `Subject`, `Date`, `Message-ID`, `Sender`, the content. `AiosmtplibMailer`
  sends them, and gives the server its addresses itself rather than reading
  them from the headers.

## [0.1.0] - 2026-11-16
### Added
- Started ingot-mail, an addon of Ingots for the mail of its applications, for
  `ingots` 0.34. Its skeleton: `MailProject`, the project of the defaults with
  the addon's `MailSettingsUnit`, whose `MailConfigs` add `MAIL_LOGGING_LEVEL`,
  `MailLoggingUnit`, which adds the logger `ingot_mail` at that level, and
  `MailUnit`, the mail, empty yet; `python -m ingot_mail` runs it on its own.
  The development automation of the ecosystem comes with it: `make check`
  (lint, tests on the working tree and on the built wheel for every supported
  Python, coverage, changelog check), towncrier news fragments, and the `ci`
  and `release` workflows.
