""" PDF Converter
"""
from zope.interface import implements
from eea.converter.interfaces import IHtml2Pdf

class Html2Pdf(object):
    """ Abstract HTML to PDF utility
    """
    implements(IHtml2Pdf)
