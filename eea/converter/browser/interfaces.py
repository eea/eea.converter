""" Browser interfaces
"""
from zope.interface import Interface

class ISupport(Interface):
    """ PDF Support
    """
    def can_download():
        """ Can download item as PDF
        """
