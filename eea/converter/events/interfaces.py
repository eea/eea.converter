""" Events
"""
from zope.component.interfaces import IObjectEvent

class IEvent(IObjectEvent):
    """ Base Event Interface for all export events
    """

class IExportSuccess(IEvent):
    """ Export succeeded
    """

class IExportFail(IEvent):
    """ Export failed
    """

class IAsyncEvent(IEvent):
    """ Base Event Interface for all Async events
    """

class IAsyncExportSuccess(IAsyncEvent):
    """ Async job for export succeeded
    """

class IAsyncExportFail(IAsyncEvent):
    """ Async job for export failed
    """
