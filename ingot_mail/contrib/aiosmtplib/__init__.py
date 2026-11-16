"""
The mailer of SMTP on aiosmtplib, with the extra ``aiosmtplib``: an
application declares it in the slot of its mail,
``mailer = Slot(AiosmtplibMailer)``, and sets the server by
``MAIL_SMTP_*``.
"""

__all__ = ("AiosmtplibMailer",)

import datetime
import email.message
import email.utils
import logging
import ssl
import typing as t

import aiosmtplib

from ingot_mail.mail import BaseMailer, Mail, MailDeliveryError
from ingot_mail.settings.configs import MailSmtpTls

logger = logging.getLogger(__name__)


class AiosmtplibMailer(BaseMailer):
    """
    Sends a mail by SMTP, a connection a mail: it connects, secures the
    connection, logs in, sends and quits. A subclass reads other configs by
    the hooks, ``_get_host()`` and the rest.
    """

    @t.override
    async def _send(self, mail: Mail, sender: str) -> None:
        message = self._build_message(mail, sender)
        tls = self._get_tls()
        user = self._get_user()
        try:
            refused, _ = await aiosmtplib.send(
                message,
                hostname=self._get_host(),
                port=self._get_port(),
                username=user or None,
                password=self._get_password() if user else None,
                use_tls=tls is MailSmtpTls.TLS,
                start_tls=tls is MailSmtpTls.STARTTLS,
                tls_context=self._get_tls_context(),
                timeout=self._get_timeout(),
            )
        except aiosmtplib.SMTPRecipientsRefused as error:
            codes = [refusal.code for refusal in error.recipients]
            raise MailDeliveryError.for_reason(
                "every address refused", is_transient=_are_transient(codes)
            ) from error
        except aiosmtplib.SMTPResponseException as error:
            raise MailDeliveryError.for_reason(
                f"{error.code} {error.message}",
                is_transient=_are_transient([error.code]),
            ) from error
        except OSError as error:
            # no connection, a connection lost, a timeout
            raise MailDeliveryError.for_reason(str(error), is_transient=True) from error
        except aiosmtplib.SMTPException as error:
            # what the server cannot do: STARTTLS, a login, an address of UTF-8
            raise MailDeliveryError.for_reason(
                str(error), is_transient=False
            ) from error
        if refused:
            logger.warning(
                "sent the mail %s, %d of its addresses refused",
                message["Message-ID"],
                len(refused),
            )
        else:
            logger.info("sent the mail %s", message["Message-ID"])

    def _build_message(self, mail: Mail, sender: str) -> email.message.EmailMessage:
        """The message of the mail, its id of the domain of the sender."""
        message = email.message.EmailMessage()
        message["From"] = sender
        message["To"] = ", ".join(mail.to)
        message["Subject"] = mail.subject
        message["Date"] = email.utils.format_datetime(
            datetime.datetime.now(datetime.UTC)
        )
        domain = sender.rpartition("@")[2] or None
        message["Message-ID"] = email.utils.make_msgid(domain=domain)
        message.set_content(mail.text)
        return message

    def _get_host(self) -> str:
        return self.project.settings.configs.MAIL_SMTP_HOST

    def _get_port(self) -> int:
        return self.project.settings.configs.MAIL_SMTP_PORT

    def _get_user(self) -> str:
        """The user to log in as; empty, no authentication."""
        return self.project.settings.configs.MAIL_SMTP_USER

    def _get_password(self) -> str:
        return self.project.settings.configs.MAIL_SMTP_PASSWORD

    def _get_tls(self) -> MailSmtpTls:
        return self.project.settings.configs.MAIL_SMTP_TLS

    def _get_tls_context(self) -> ssl.SSLContext | None:
        """
        The context of TLS; ``None``, that of the system, verifying the
        certificate of the server by its roots.
        """
        return None

    def _get_timeout(self) -> float:
        """Seconds to wait for the server, at each step."""
        return self.project.settings.configs.MAIL_SMTP_TIMEOUT


def _are_transient(codes: list[int]) -> bool:
    """A reply 4xx asks to try again later; 5xx, never."""
    return all(400 <= code < 500 for code in codes)
