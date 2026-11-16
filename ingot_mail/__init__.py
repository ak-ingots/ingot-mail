"""
ingot-mail: the mail of Ingots applications. An application inherits from
:class:`MailProject`, or joins the units of the addon, ``settings``,
``logging`` and ``mail``, with those of its other addons.
"""

__all__ = ("MailProject",)

from .project import MailProject
