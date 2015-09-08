""" Metadata updater
"""
import os
import tempfile
import logging
from subprocess import Popen, PIPE, STDOUT

from zope import interface
from eea.reports.pdf.interfaces import IPDFMetadataUpdater
from eea.reports.pdf.config import META_TEMPLATE
from eea.reports.pdf import CAN_UPDATE_PDF_METADATA

logger = logging.getLogger('eea.reports.pdf.updater')

class PDFMetadataUpdater(object):
    """ Update pdfs metadata using external pdftk tool.
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
        except RuntimeError, err:
            logger.debug('METADATA NOT FIXED: %s: pdf %s, lang %s',
                         err, pdf_id, pdf_lang)
        except Exception, err:
            logger.warn('METADATA NOT FIXED: %s: pdf %s, lang %s',
                        err, pdf_id, pdf_lang)
        else:
            logger.debug('PDF: %s, lang: %s updated with metadata: %s',
                         pdf_id, pdf_lang, metadata)
        return pdf
    #
    # Private
    #
    def _update(self, pdf, metadata):
        """ Update given pdf with given metadata.
        """
        if not self._can_convert():
            raise RuntimeError('pdftk tool is not installed')

        if getattr(pdf, 'read', None):
            tmpdata = pdf.read()
            pdf.seek(0)
            pdf = tmpdata

        if not pdf:
            raise ValueError('Empty pdf file')

        metadata = self._process_metadata(metadata)
        metadata = metadata.encode('utf-8')

        if not metadata:
            raise ValueError('Empty metadata provided')

        tmp_in = tempfile.mktemp(suffix='.pdf')
        tmp_out = tempfile.mktemp(suffix='.pdf')
        tmp_meta = tempfile.mktemp(suffix='.txt')

        open(tmp_meta, 'w').write(metadata)
        open(tmp_in, 'wb').write(pdf)

        # Run pdftk
        cmd = 'pdftk %s update_info %s output %s' % (tmp_in, tmp_meta, tmp_out)
        logger.debug(cmd)
        process = Popen(cmd, shell=True,
                        stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        res = process.stdout.read()
        if res:
            logger.debug(res)

        # Get results
        data = open(tmp_out, 'rb').read()

        # Cleanup
        self._finish(tmp_in, tmp_out, tmp_meta)

        # Return
        if not data:
            raise ValueError('Empty pdf output')
        return data
    #
    # Utils
    #
    def _can_convert(self):
        """ Check if pdftk is installed
        """
        return CAN_UPDATE_PDF_METADATA

    def _utf2entity(self, data=''):
        """ Convert utf stream to html entities
        """
        res = []
        for x in data:
            if ord(x) > 128:
                x = '&#%d;' % ord(x)
            res.append(x)
        return u''.join(res)

    def _process_metadata(self, metadata):
        """ Returns metadata as string of this format in order to be imported
        using pdftk <pdffile> update_info <metadata.txt> output <output.pdf>.
        [...]
        InfoKey: Creator
        InfoValue: Adobe InDesign CS2 (4.0.2)
        [...]
        """
        # Process list/tuple metadata
        keywords = list(metadata.get('keywords', []))
        themes = list(metadata.get('themes', []))
        keywords.extend([x for x in themes if x not in keywords])
        metadata['keywords_str'] = '; '.join(keywords)

        authors = metadata.get('creators', [])
        metadata['authors_str'] = '; '.join(authors)

        publishers = metadata.get('publishers', [])
        metadata['publishers_str'] = '; '.join(publishers)

        serial_title = metadata.get('serial_title_alt', u'')
        if not serial_title:
            st_number = metadata.get('serial_title_number', 0)
            st_type = metadata.get('serial_title_type', '')
            st_year = metadata.get('serial_title_year', 1970)
            serial_title = '%s %s/%s' % (st_type, st_number, st_year)
        metadata['serial_title_str'] = serial_title

        # Convert non-ascii chart to html entities
        res = {}
        for key, value in metadata.items():
            if value is None:
                res[key] = ''
            elif isinstance(value, int) or isinstance(value, float):
                res[key] = value
            elif isinstance(value, str) or isinstance(value, unicode):
                try:
                    value = value.decode('utf-8')
                except UnicodeDecodeError:
                    value = self._utf2entity(value)
                except Exception, err:
                    # Not string or unicode
                    logger.debug(err)
                else:
                    value = self._utf2entity(value)
                res[key] = value

        # Return
        return META_TEMPLATE % res

    def _finish(self, *paths):
        """ remove temporary files
        """
        for path in paths:
            try:
                os.remove(path)
            except Exception, err:
                logger.warn(err)
