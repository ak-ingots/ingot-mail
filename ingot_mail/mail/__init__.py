"""The mail unit: the mail of the project."""

__all__ = ("MailUnit",)

from ingots.puer import Unit


class MailUnit(Unit):
    """
    The mail in the project, empty yet. An application extending it declares
    a subclass of this unit in the slot ``mail`` of its project.
    """
