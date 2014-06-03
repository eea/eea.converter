""" Download as PDF
"""
import os
import logging
from subprocess import Popen, PIPE, STDOUT

from zope.component import queryMultiAdapter, queryAdapter
from collective.sendaspdf.browser.download import PreDownloadPDF
from collective.sendaspdf.interfaces import ISendAsPDFOptionsMaker
from eea.converter import CAN_JOIN_PDFS

logger = logging.getLogger('eea.converter')

class Pdf(PreDownloadPDF):
    """ Download as PDF using @@pdf.cover and @@pdf.body browser views
    """
    def __init__(self, context, request):
        super(Pdf, self).__init__(context, request)
        self.filename = ''
        self._cover = None
        self._body = None
        self._backcover = None
        self._disclaimer = None

    @property
    def cover(self):
        """ PDF cover page
        """
        if not self._cover:
            self.request.URL0 = "pdf.cover" # pdf.print.css requirement
            self._cover = queryMultiAdapter((self.context, self.request),
                                            name=u'pdf.cover')
        return self._cover

    @property
    def disclaimer(self):
        """ PDF disclaimer, first page after cover
        """
        if not self._disclaimer:
            self._disclaimer = queryMultiAdapter((self.context, self.request),
                                                 name=u'pdf.disclaimer')
        return self._disclaimer

    @property
    def body(self):
        """ PDF body pages
        """
        if not self._body:
            self._body = queryMultiAdapter((self.context, self.request),
                                           name=u'pdf.body')
        return self._body

    @property
    def backcover(self):
        """ PDF back cover
        """
        if not self._backcover:
            self._backcover = queryMultiAdapter((self.context, self.request),
                                                name=u'pdf.cover.back')
        return self._backcover

    def _cover_get_adapter_options(self):
        """ Get options per
        """
        options = queryAdapter(
            self.context, ISendAsPDFOptionsMaker, name='pdf.cover',
            default=queryAdapter(self.context, ISendAsPDFOptionsMaker))

        if not options:
            return {}, None
        return options.getOptions(), options.overrideAll()

    def _disclaimer_get_adapter_options(self):
        """ Get options per
        """
        options = queryAdapter(
            self.context, ISendAsPDFOptionsMaker, name='pdf.disclaimer',
            default=queryAdapter(self.context, ISendAsPDFOptionsMaker))

        if not options:
            return {}, None
        return options.getOptions(), options.overrideAll()

    def _backcover_get_adapter_options(self):
        """ Get options per
        """
        options = queryAdapter(
            self.context, ISendAsPDFOptionsMaker, name='pdf.cover.back',
            default=queryAdapter(self.context, ISendAsPDFOptionsMaker))

        if not options:
            return {}, None
        return options.getOptions(), options.overrideAll()

    def make_pdf_cover(self):
        """ Separate method for creating pdf cover
        """
        if not self.cover:
            return ''

        self._get_adapter_options = self._cover_get_adapter_options
        self.generate_pdf_file(self.cover())
        return os.path.join(self.tempdir, self.filename)

    def make_pdf_body(self):
        """ Separate method for creating pdf body
        """
        if not self.body:
            return ''

        self._get_adapter_options = super(Pdf, self)._get_adapter_options
        self.generate_pdf_file(self.body())
        return os.path.join(self.tempdir, self.filename)

    def make_pdf_disclaimer(self):
        """ Separate method for creating pdf disclaimer
        """
        if not self.disclaimer:
            return ''

        self._get_adapter_options = self._disclaimer_get_adapter_options()
        self.generate_pdf_file(self.disclaimer())
        return os.path.join(self.tempdir, self.filename)

    def make_pdf_backcover(self):
        """ Separate method for creating pdf back cover
        """
        if not self.backcover:
            return ''

        self._get_adapter_options = self._backcover_get_adapter_options
        self.generate_pdf_file(self.backcover())
        return os.path.join(self.tempdir, self.filename)

    def make_pdf(self):
        """ Override pdf converter
        """
        if not CAN_JOIN_PDFS:
            return super(Pdf, self).make_pdf()

        # Generate pdf cover
        cover = self.make_pdf_cover()

        # Generate pdf disclaimer
        disclaimer = self.make_pdf_disclaimer()

        # Generate pdf body
        body = self.make_pdf_body()

        # Generate pdf back cover
        backcover = self.make_pdf_backcover()

        # Join cover, body and backcover
        self.filename = self.generate_temp_filename()
        output = os.path.join(self.tempdir, self.filename)

        cmd = "pdftk %s %s %s %s output %s" % (
            cover, disclaimer, body, backcover, output
        )

        logger.debug(cmd)

        process = Popen(
            cmd, shell=True, stdin=PIPE, stdout=PIPE,
            stderr=STDOUT, close_fds=True)

        res = process.stdout.read()
        if res:
            logger.debug(res)

        # Return
        self.pdf_tool.registerPDF(self.filename)
        self.pdf_file = file(output, 'r')
        self.pdf_file.close()

    def __call__(self, **kwargs):
        # Cheat condition @@plone_context_state/is_view_template
        self.request['ACTUAL_URL'] = self.context.absolute_url()
        return super(Pdf, self).__call__(**kwargs)
