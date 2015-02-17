""" Async events
"""

from zope.interface import implementer
from eea.converter.events.interfaces import IAsyncExportFail
from eea.converter.events.interfaces import IAsyncExportSuccess
from eea.converter.events import AsyncEvent

@implementer(IAsyncExportFail)
class AsyncExportFail(AsyncEvent):
    """ Event triggered when an async export job failed
    """

@implementer(IAsyncExportSuccess)
class AsyncExportSuccess(AsyncEvent):
    """ Event triggered when an async export job succeeded
    """
