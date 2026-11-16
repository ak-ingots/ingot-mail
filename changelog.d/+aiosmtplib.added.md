The mailer of SMTP, `AiosmtplibMailer` of `ingot_mail.contrib.aiosmtplib`,
with the extra `aiosmtplib`: a connection a mail, configured by
`MAIL_SMTP_HOST`, `MAIL_SMTP_PORT`, `MAIL_SMTP_USER`, `MAIL_SMTP_PASSWORD`,
`MAIL_SMTP_TLS` (`STARTTLS` by default, `TLS` or `NONE`) and
`MAIL_SMTP_TIMEOUT`, read by hooks a subclass overrides. A failure is
`MailDeliveryError`, transient for no connection, a timeout or a reply 4xx.
The logger `ingot_mail` tells each mail sent by its message id alone.
