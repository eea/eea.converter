""" PDF Views
"""
from Products.Five.browser import BrowserView
from eea.converter.utils import truncate

class Cover(BrowserView):
    """ PDF Cover
    """
    def truncate(self, text, length=300, orphans=10, suffix=u".", end=u"."):
        """
        Truncate text by the number of characters without cutting words at
        the end.

        Orphans is the number of trailing chars not to cut, for example

        If end char provided try to separate by it
        """
        return truncate(text, length, orphans, suffix, end)


class Body(BrowserView):
    """ PDF Body
    """
    def __call__(self, **kwargs):

        layout = self.context.getLayout()
        if not layout:
            return self.index()

        try:
            view = self.context.restrictedTraverse(layout)
        except Exception:
            return self.index()

        return view()

class Header(BrowserView):
    """ PDF Header
    """

class Footer(BrowserView):
    """ PDF Footer
    """
