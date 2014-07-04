""" Converter interfaces
"""
from zope.interface import Interface

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
