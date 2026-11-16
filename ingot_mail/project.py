"""The project of the addon: what an application inherits from."""

__all__ = ("MailProject",)

from ingots.defaults import Project
from ingots.puer import Slot

from .logging import MailLoggingUnit
from .mail import MailUnit
from .settings import MailSettingsUnit


class MailProject(Project):
    """
    The project of the defaults with the addon's :class:`MailSettingsUnit`,
    :class:`MailLoggingUnit` and the mail, :class:`MailUnit`. An application
    inherits from it and sets its own ``env_configs_prefix``; the addon run on
    its own (``python -m ingot_mail``) keeps the prefix of the defaults,
    ``INGOT``.
    """

    settings = Slot(MailSettingsUnit)
    logging = Slot(MailLoggingUnit)
    mail = Slot(MailUnit)
