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

    # BBB
    def make_pdf_cover(self, **kwargs):
        """ Return path to PDF cover
        """
        pdf = self.make_cover(**kwargs)
        return pdf.path if pdf else ''

    def make_cover(self, dry_run=False, **kwargs):
        """
        Unfortunately wkhtmltopdf can't make cover and body with different
        margins, thus generate them separately
        """
        cover = self.options('pdf.cover')
        cover = cover()
        if not cover:
            return None

        options = self.options('')
        options._margin = False
        options._cookies = self.cookies
        timeout = options.timeout

        options = options()
        options.extend(cover)

        html2pdf = queryUtility(IHtml2Pdf)
        return html2pdf(options, timeout, dry_run)

    def make_back_cover(self, dry_run=False, **kwargs):
        """ Back cover
        """
        cover = self.options('pdf.cover.back')
        cover = cover()
        if not cover:
            return None

        options = self.options('')
        options._margin = False
        options._cookies = self.cookies
        timeout = options.timeout

        options = options()
        options.extend(cover)

        html2pdf = queryUtility(IHtml2Pdf)
        return html2pdf(options, timeout, dry_run)

    def make_disclaimer(self, dry_run=False, **kwargs):
        """
        Generate pdf disclaimer
        """
        disclaimer = self.options('pdf.disclaimer')
        disclaimer = disclaimer()
        if not disclaimer:
            return None

        options = self.options('')
        options._margin = False
        options._cookies = self.cookies
        timeout = options.timeout

        options = options()
        options.extend(disclaimer)

        html2pdf = queryUtility(IHtml2Pdf)
        return html2pdf(options, timeout, dry_run)

    def make_body(self, dry_run=False, **kwargs):
        """ Override pdf converter
        """
        body = self.options('pdf.body')
        toc = body.toc
        toc_links = body.toc_links

        body = body()
        if not body:
            return None

        options = self.options('')
        options._cookies = self.cookies
        options._outline = toc_links
        timeout = options.timeout

        options = options()
        options.extend(body)

        cleanup = [toc] if toc else []
        html2pdf = queryUtility(IHtml2Pdf)
        return html2pdf(options, timeout, dry_run, cleanup=cleanup)

    def make_concat(self, dependencies, default='', dry_run=False, **kwargs):
        """ Concat pdfs
        """
        timeout = self.options('').timeout
        html2pdf = queryUtility(IHtml2Pdf)
        return html2pdf.concat(dependencies, default=default,
                               timeout=timeout, dry_run=dry_run)


    def make_pdf(self, dry_run=False, **kwargs):
        """ Compute pdf
        """
        dependencies = []

        cover = self.make_cover(dry_run=True)
        if cover:
            dependencies.append(cover)

        disclaimer = self.make_disclaimer(dry_run=True)
        if disclaimer:
            dependencies.append(disclaimer)

        body = self.make_body(dry_run=True)
        if body:
            dependencies.append(body)

        backcover = self.make_back_cover(dry_run=True)
        if backcover:
            dependencies.append(backcover)

        converter = self.make_concat(dependencies, default=body, dry_run=True)

        if dry_run:
            return converter

        data = ''
        if not converter:
            return data

        converter.run()
        output = converter.path
        if output and os.path.exists(output):
            data = open(output, 'rb').read()

        converter.cleanup()
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
        if not getattr(support, 'can_download', lambda: False)():
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
