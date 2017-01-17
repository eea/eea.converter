""" PDF Views
"""
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from eea.converter.utils import truncate
from eea.converter.config import EEAMessageFactory as _

class Cover(BrowserView):
    """ PDF Cover
    """
    template = ViewPageTemplateFile('../zpt/pdf.cover.pt')

    def truncate(self, text, length=300, orphans=10,
                 suffix=u".", end=u".", cut=True, **kwargs):
        """
        Truncate text by the number of characters without cutting words at
        the end.

        Orphans is the number of trailing chars not to cut, for example

        If end char provided try to separate by it
        """
        return truncate(text, length, orphans, suffix, end, cut)

    def __call__(self, **kwargs):
        return self.template()

class Disclaimer(Cover):
    """ PDF Disclaimer
    """
    template = ViewPageTemplateFile('../zpt/pdf.disclaimer.pt')

class Toc(Cover):
    """ PDF Table of Contents
    """
    template = ViewPageTemplateFile('../zpt/pdf.toc.pt')

    @property
    def toc_links(self):
        """ Enable Table of contents links
        """
        return True

    @property
    def toc_depth(self):
        """
        :return: Toc depth
        :rtype: int
        """
        return getattr(self.context, 'tocdepth', -1)

    @property
    def header(self):
        """ Header
        """
        contents_translate = _(u"Contents")
        return contents_translate

class BackCover(Cover):
    """ PDF Back Cover
    """
    template = ViewPageTemplateFile('../zpt/pdf.cover.back.pt')


class Body(Cover):
    """ PDF Body
    """
    template = ViewPageTemplateFile('../zpt/pdf.body.pt')
    macro = ViewPageTemplateFile('../zpt/pdf.macro.pt')


    def __call__(self, **kwargs):
        kwargs.update(self.request.form)

        layout = self.context.getLayout()
        if not layout:
            return self.template()

        try:
            view = self.context.restrictedTraverse(layout)
        except Exception:
            return self.template()

        macro = kwargs.get('macro', None)
        if macro:
            try:
                macro = view.macros[macro]
            except Exception:
                return ''
            else:
                return self.macro(macro=macro)

        return view()

class Header(Cover):
    """ PDF Header
    """
    template = ViewPageTemplateFile('../zpt/pdf.header.pt')

    @property
    def body(self):
        """ Header body
        """
        text = self.request.get('subsection', '')
        text = self.truncate(text, 75, 5, suffix='')
        return text

class Footer(Cover):
    """ PDF Footer
    """
    template = ViewPageTemplateFile('../zpt/pdf.footer.pt')

    @property
    def body(self):
        """ Footer body
        """
        text = self.request.get('section', '')
        text = self.truncate(text, 75, 5, suffix='')
        return text
