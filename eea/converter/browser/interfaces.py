""" Browser interfaces
"""
from zope.interface import Interface
from zope import schema

class ISupport(Interface):
    """ PDF Support
    """
    can_download = schema.Bool(
        u"Can download item as PDF",
        readonly=True
    )
