""" Metadata updater
"""
import logging

from StringIO import StringIO
from PyPDF2 import PdfFileWriter, PdfFileReader
from zope import interface
from zope.component.hooks import getSite
from eea.converter.interfaces import IPDFMetadataUpdater

logger = logging.getLogger('eea.converter')

class PDFMetadataUpdater(object):
    """ Update pdfs metadata
    """
    interface.implements(IPDFMetadataUpdater)
    #
    # Public interface
    #
    def update(self, pdf, metadata):
        """ Update pdf file with given metadata and return it. See interface
            for more details.
        """
        pdf_id = metadata.get('id', '')
        pdf_lang = metadata.get('lang', '')
        try:
            pdf = self._update(pdf, metadata)
        except Exception, err:
            logger.warn('METADATA NOT FIXED: pdf %s, lang %s', pdf_id, pdf_lang)
            logger.exception(err)
        return pdf
    #
    # Private
    #
    def _update(self, pdf, metadata):
        """ Update given pdf with given metadata.
        """
        metadata = self._process_metadata(metadata)
        reader = PdfFileReader(pdf)
        writer = PdfFileWriter()
        writer.appendPagesFromReader(reader)
        writer.addMetadata(metadata)
        output = StringIO()
        writer.write(output)
        return output

    def _process_metadata(self, metadata):
        """ Prepare metadata for PDF
        """
        output = {}

        # Title
        if metadata.get('title', ''):
            output[u"/Title"] = metadata['title']

        # Subject
        if metadata.get('description', ''):
            output[u"/Subject"] = metadata['description']

        # Keywords, Themes
        keywords = list(metadata.get('keywords', []))
        themes = list(metadata.get('themes', []))
        keywords.extend([x for x in themes if x not in keywords])

        if keywords:
            output[u"/Keywords"] = keywords
            output[u"/Themes"] = keywords

        # Creator, Authors
        if metadata.get('creators', []):
            creators = metadata['creators']
            output[u"/Creator"] = creators
            output[u"/Authors"] = creators

        site = getSite()
        if getattr(site, 'absolute_url', None):
            output[u"/Producer"] = site.absolute_url()

        if metadata.get('publishers', []):
            output[u"/Publishers"] = metadata['publishers']

        if metadata.get('isbn', ''):
            output[u"/ISBN"] = metadata['isbn']

        if metadata.get('order_id', ''):
            output[u"/OrderId"] = metadata['order_id']

        if metadata.get('copyrights', ''):
            output[u"/Copyrights"] = metadata['copyrights']

        if metadata.get('lang', ''):
            output[u"/Language"] = metadata['lang']

        if metadata.get('price', ''):
            output[u"/Price"] = metadata['price']

        serial_title = metadata.get('serial_title_alt', '')
        if not serial_title:
            st_number = metadata.get('serial_title_number', 0)
            st_type = metadata.get('serial_title_type', '')
            st_year = metadata.get('serial_title_year', 1970)
            serial_title = u"%s %s/%s" % (st_type, st_number, st_year)

        if serial_title:
            output[u"/SerialTitle"] = serial_title

        for key, value in output.items():
            if isinstance(value, str):
                output[key] = value.decode('utf-8')
            if isinstance(value, (int, float)):
                output[key] = u"%s" % value
            if isinstance(value, (tuple, list)):
                output[key] = u"; ".join(value)
        return output
