The headers of a mail, `Mail.headers`, the application's own,
`X-Request-ID` for one: `send()` refuses a name not of printable ASCII or
with a colon, a value with a character not printable, and a header the
mailer sets or that tells where the mail goes, `From`, `To`, `Cc`, `Bcc`,
`Subject`, `Date`, `Message-ID`, `Sender`, the content. `AiosmtplibMailer`
sends them, and gives the server its addresses itself rather than reading
them from the headers.
