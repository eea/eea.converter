""" PDF Support
"""
from zope.interface import implementer
from Products.Five.browser import BrowserView
from eea.converter.interfaces import ISupport
from eea.converter.config import ASYNC

@implementer(ISupport)
class Support(BrowserView):
    """ PDF Support
    """
    def can_download(self):
        """ Override this adapter in order to restrict access to PDF download
        """
        return True

    def async(self):
        """ Async download
        """
        return ASYNC()

    def email(self):
        """ User has email
        """
        return u''
