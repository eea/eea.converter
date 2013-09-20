""" PDF Views
"""
from Products.Five.browser import BrowserView

class Cover(BrowserView):
    """ PDF Cover
    """

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
