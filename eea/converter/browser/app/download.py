""" Download as PDF
"""
import os
import logging

from Products.Five.browser import BrowserView
from zope.publisher.interfaces import NotFound
from zope.component import queryAdapter, queryUtility, queryMultiAdapter
from Products.statusmessages.interfaces import IStatusMessage
from eea.converter.interfaces import IPDFOptionsMaker, IHtml2Pdf

logger = logging.getLogger('eea.converter')

class Pdf(BrowserView):
    """ Download as PDF using @@pdf.cover and @@pdf.body browser views
    """
    def __init__(self, context, request):
        super(Pdf, self).__init__(context, request)
        self._cookies = None

    @property
    def cookies(self):
        """ Cookies
        """
        if self._cookies is None:
            ac_cookie = self.request.cookies.get('__ac', None)
            if not ac_cookie:
                self._cookies = {}
                return self._cookies

            self._cookies = {'__ac': ac_cookie}
        return self._cookies

    def options(self, section=u'', margin=True):
        """ Get options for given section
        """
        return queryAdapter(self.context, IPDFOptionsMaker, name=section)

    def make_cover(self):
        """
        Unfortunately wkhtmltopdf can't make cover and body with different
        margins, thus generate them separately
        """
        cover = self.options('pdf.cover')
        cover = cover()
        if not cover:
            return ''

        options = self.options('')
        options._margin = False
        options._cookies = self.cookies
        timeout = options.timeout

        options = options()
        options.extend(cover)

        html2pdf = queryUtility(IHtml2Pdf)
        return html2pdf(options, timeout)

    # BBB
    make_pdf_cover = make_cover

    def make_back_cover(self):
        """ Back cover
        """
        cover = self.options('pdf.cover.back')
        cover = cover()
        if not cover:
            return ''

        options = self.options('')
        options._margin = False
        options._cookies = self.cookies
        timeout = options.timeout

        options = options()
        options.extend(cover)

        html2pdf = queryUtility(IHtml2Pdf)
        return html2pdf(options, timeout)

    def make_disclaimer(self):
        """
        Generate pdf disclaimer
        """
        disclaimer = self.options('pdf.disclaimer')
        disclaimer = disclaimer()
        if not disclaimer:
            return ''

        options = self.options('')
        options._margin = False
        options._cookies = self.cookies
        timeout = options.timeout

        options = options()
        options.extend(disclaimer)

        html2pdf = queryUtility(IHtml2Pdf)
        return html2pdf(options, timeout)

    def make_body(self):
        """ Override pdf converter
        """
        body = self.options('pdf.body')
        toc = body.toc
        toc_links = body.toc_links

        body = body()
        if not body:
            return ''

        options = self.options('')
        options._cookies = self.cookies
        options._outline = toc_links
        timeout = options.timeout

        options = options()
        options.extend(body)

        html2pdf = queryUtility(IHtml2Pdf)
        output = html2pdf(options, timeout)

        # Cleanup possible temp toc file
        if toc:
            html2pdf.cleanup(toc)

        return output

    def make_pdf(self):
        """ Compute pdf
        """
        pdfs = []

        cover = self.make_cover()
        if cover:
            pdfs.append(cover)

        disclaimer = self.make_disclaimer()
        if disclaimer:
            pdfs.append(disclaimer)

        body = self.make_body()
        if body:
            pdfs.append(body)

        backcover = self.make_back_cover()
        if backcover:
            pdfs.append(backcover)

        timeout = self.options('').timeout
        html2pdf = queryUtility(IHtml2Pdf)

        data = ''
        if not pdfs:
            return data
        elif len(pdfs) == 1:
            output = pdfs.pop(0)
        else:
            output = html2pdf.concat(pdfs[:], default=body, timeout=timeout)

        if output and os.path.exists(output):
            data = open(output, 'rb').read()
            pdfs.append(output)

        html2pdf.cleanup(*pdfs)
        return data

    @property
    def filename(self):
        """ Generates the name for the PDF file.
        If the context title does not contain non-ascii characters,
        we'll use it.
        Otherwise we'll rewrite it using normalize string.
        """
        try:
            name = self.context.title.encode('ascii')
        except (UnicodeDecodeError, UnicodeEncodeError, ):
            name = self.context.id
        return '%s.pdf' % name

    def __call__(self, **kwargs):

        support = queryMultiAdapter((self.context, self.request),
                                    name='pdf.support')
        if not getattr(support, 'can_download', None):
            raise NotFound(self.context, self.__name__, self.request)

        # Cheat condition @@plone_context_state/is_view_template
        self.request['ACTUAL_URL'] = self.context.absolute_url()

        data = self.make_pdf()
        if not data:
            IStatusMessage(self.request).addStatusMessage(
                "An error occurred while downloading your PDF file. "
                "Please try again later.",
                type='error')
            return self.request.response.redirect(self.context.absolute_url())


        self.request.response.setHeader("Content-type", "application/pdf")
        self.request.response.setHeader("X-Robots-Tag", "noindex")
        self.request.response.setHeader('Content-Disposition',
            'attachment; filename="%s"' % self.filename
        )
        return data
