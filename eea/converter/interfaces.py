""" Converter interfaces
"""
from zope.interface import Interface
from eea.converter.browser.interfaces import ISupport

class IConvert(Interface):
    """ Convert images using ImageMagick
    """
    def __call__(data, data_from=".pdf", data_to=".png", **kwargs):
        """ Try to convert raw data to given file type
        """

class IWatermark(Interface):
    """ Place watermarks using PIL
    """

class IPDFOptionsMaker(Interface):
    """ PDF Options Maker
    """
    def __call__():
        """
        :return: a list of wkhtmltopdf Page Options
        See http://wkhtmltopdf.org/usage/wkhtmltopdf.txt
        """

class IHtml2Pdf(Interface):
    """ HTML to PDF utility
    """

__all__ = [
    ISupport.__name__,
    IConvert.__name__,
    IWatermark.__name__,
    IPDFOptionsMaker.__name__,
    IHtml2Pdf.__name__
]
