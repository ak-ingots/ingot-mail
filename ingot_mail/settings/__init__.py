"""The settings unit of the defaults with the configs of the addon."""

__all__ = ("MailSettingsUnit",)

from ingots.defaults.settings import SettingsUnit
from ingots.puer import Slot

from .configs import MailConfigs


class MailSettingsUnit(SettingsUnit):
    """The settings unit, with the addon's :class:`MailConfigs`."""

    configs = Slot(MailConfigs)
