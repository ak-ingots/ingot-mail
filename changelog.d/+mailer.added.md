The mail and its mailer: `Mail`, a mail of plain text, its addresses and its
text out of the `repr`; `BaseMailer`, the slot `mailer` of `MailUnit`,
abstract, whose `send()` refuses a header unfit to send by `MailHeaderError`
before the backend, the sender that of the mail or `MAIL_FROM`; a mail not
delivered is `MailDeliveryError`, transient or not. `MemoryMailer` of
`ingot_mail.contrib.memory` keeps the mail for the tests, and
`python -m ingot_mail` runs with it; `MailerContract` of
`ingot_mail.testing.contracts` is what a backend guarantees.
