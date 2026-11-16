Started ingot-mail, an addon of Ingots for the mail of its applications, for
`ingots` 0.34. Its skeleton: `MailProject`, the project of the defaults with
the addon's `MailSettingsUnit`, whose `MailConfigs` add `MAIL_LOGGING_LEVEL`,
`MailLoggingUnit`, which adds the logger `ingot_mail` at that level, and
`MailUnit`, the mail, empty yet; `python -m ingot_mail` runs it on its own.
The development automation of the ecosystem comes with it: `make check`
(lint, tests on the working tree and on the built wheel for every supported
Python, coverage, changelog check), towncrier news fragments, and the `ci`
and `release` workflows.
