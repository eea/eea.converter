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
    def body(self):
        """ PDF body pages
        """
        if not self._body:
            self._body = queryMultiAdapter((self.context, self.request),
                                           name=u'pdf.body')
        return self._body

    def _cover_get_adapter_options(self):
        """ Get options per
        """
        options = queryAdapter(
            self.context, ISendAsPDFOptionsMaker, name='pdf.cover',
            default=queryAdapter(self.context, ISendAsPDFOptionsMaker))

        if not options:
            return {}, None
        return options.getOptions(), options.overrideAll()

    def make_pdf_cover(self):
        """ Separate method for creating pdf cover
        """
        self._get_adapter_options = self._cover_get_adapter_options
        self.generate_pdf_file(self.cover())
        return os.path.join(self.tempdir, self.filename)

    def make_pdf(self):
        """ Override pdf converter
        """
        if not CAN_JOIN_PDFS:
            return super(Pdf, self).make_pdf()

        # Generate pdf cover
        cover = self.make_pdf_cover()

        # Generate pdf body
        self._get_adapter_options = super(Pdf, self)._get_adapter_options
        self.generate_pdf_file(self.body())
        body = os.path.join(self.tempdir, self.filename)

        # Join cover and body
        self.filename = self.generate_temp_filename()
        output = os.path.join(self.tempdir, self.filename)

        cmd = "pdftk %s %s output %s" % (cover, body, output)
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
