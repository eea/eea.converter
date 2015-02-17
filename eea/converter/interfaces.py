""" Converter interfaces
"""
from zope import schema
from zope.interface import Interface
from eea.converter.browser.interfaces import ISupport

# Events
from eea.converter.events.interfaces import IEvent
from eea.converter.events.interfaces import IExportFail
from eea.converter.events.interfaces import IExportSuccess
from eea.converter.events.interfaces import IAsyncEvent
from eea.converter.events.interfaces import IAsyncExportFail
from eea.converter.events.interfaces import IAsyncExportSuccess
from eea.converter.config import EEAMessageFactory as _

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


class IContextWrapper(Interface):
    """ Context wrapper used by async events
    """


class IAsyncJob(Interface):
    """ Asynchronous job
    """
    toclean = schema.List(
        title=_(u"List of absolute file paths on disk to be cleaned up"),
        value_type=schema.TextLine(title=_(u"Absolute file path on disk"))
    )

    path = schema.TextLine(
        title=_(u"Output file path on disk")
    )

    dependencies = schema.List(
        title=_(u"List of jobs to be ran as dependencies to this job"),
        value_type=schema.Object(
            title=_(u"IAsyncJob job"),
            schema=Interface)
    )

    def cleanup():
        """ Cleanup temporary files on disk
        """

    def run():
        """ Run job
        """


__all__ = [
    ISupport.__name__,
    IConvert.__name__,
    IWatermark.__name__,
    IPDFOptionsMaker.__name__,
    IHtml2Pdf.__name__,
    IContextWrapper.__name__,
    IAsyncJob.__name__,
    IEvent.__name__,
    IExportFail.__name__,
    IExportSuccess.__name__,
    IAsyncEvent.__name__,
    IAsyncExportFail.__name__,
    IAsyncExportSuccess.__name__,
]
