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