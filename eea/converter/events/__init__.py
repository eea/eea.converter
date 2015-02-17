""" Events
"""
from zope.interface import implementer
from eea.converter.events.interfaces import IEvent, IAsyncEvent

@implementer(IEvent)
class Event(object):
    """ Abstract event
    """
    def __init__(self, context, **kwargs):
        self.object = context

@implementer(IAsyncEvent)
class AsyncEvent(Event):
    """ Abstract event for all async events
    """
