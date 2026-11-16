"""
The mail unit: the mail of the project, :class:`Mail` sent by the mailer of
the slot ``mailer``, a backend of ``ingot_mail.contrib`` the application
declares.
"""

__all__ = (
    "BaseMailer",
    "Mail",
    "MailDeliveryError",
    "MailError",
    "MailHeaderError",
    "MailUnit",
)

from ingots.puer import Slot, Unit

from .data import Mail
from .errors import MailDeliveryError, MailError, MailHeaderError
from .mailers import BaseMailer


class MailUnit(Unit):
    """
    The mail in the project: :attr:`mailer`, abstract here. An application
    declares a backend in a subclass of this unit, ``mailer =
    Slot(MemoryMailer)`` for one, in the slot ``mail`` of its project.
    """

    mailer = Slot(BaseMailer)  # type: ignore[type-abstract]
