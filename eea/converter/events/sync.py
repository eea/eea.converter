""" Sync events
"""

from zope.interface import implementer
from eea.converter.events.interfaces import IExportFail
from eea.converter.events.interfaces import IExportSuccess
from eea.converter.events import Event

@implementer(IExportFail)
class ExportFail(Event):
    """ Event triggered when an export job failed
    """

@implementer(IExportSuccess)
class ExportSuccess(Event):
    """ Event triggered when an export job succeeded
    """
