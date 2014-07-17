""" PDF Converter
"""
from zope.interface import implementer
from eea.converter.interfaces import IHtml2Pdf

@implementer(IHtml2Pdf)
class Html2Pdf(object):
    """ Abstract HTML to PDF utility
    """
