""" Browser interfaces
"""
from zope.interface import Interface
from zope import schema

class ISupport(Interface):
    """ PDF Support
    """
    def can_download():
        """ Can download item as PDF
        """
