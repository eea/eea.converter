""" Cover image
"""
import os
import tempfile
import logging
from subprocess import Popen, PIPE, STDOUT

from zope import interface
from eea.converter.interfaces import IPDFCoverImage
from eea.converter import CAN_GENERATE_COVER_IMAGE
logger = logging.getLogger('eea.reports.pdf.cover')

class PDFCoverImage(object):
    """ Generate pdf cover image using pdftk toolkit
    """
    interface.implements(IPDFCoverImage)
    #
    # Public interface
    #
    def generate(self, pdf, width=210, height=297):
        """ Safely generate image. See interface for more details.
        """
        image = None
        try:
            image = self._generate(pdf, width, height)
        except RuntimeError, err:
            logger.debug('Could not generate pdf cover image: %s', err)
        except Exception, err:
            logger.warn('Could not generate pdf cover image: %s', err)
        return image

    def _generate(self, pdf, width=210, height=297):
        """ generate image from given pdf
        """
        if not self._can_convert():
            raise RuntimeError('pdftk tool is not installed')

        if getattr(pdf, 'read', None):
            tmpdata = pdf.read()
            pdf.seek(0)
            pdf = tmpdata
        if not pdf:
            raise ValueError('Empty pdf file')

        tmp_inp = tempfile.mktemp(suffix='.pdf')
        tmp_out = tempfile.mktemp(suffix='.pdf')
        tmp_img = tempfile.mktemp(suffix='.gif')
        open(tmp_inp, 'wb').write(pdf)

        # Run pdftk
        cmd = "pdftk %s cat 1 output %s" % (tmp_inp, tmp_out)
        logger.debug(cmd)
        process = Popen(cmd, shell=True,
                        stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        res = process.stdout.read()
        if res:
            logger.debug(res)

        # Run image magick convert
        cmd = "convert %s -resize %sx%s %s" % (tmp_out, width, height, tmp_img)
        process = Popen(cmd, shell=True,
                        stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        res = process.stdout.read()
        if res:
            logger.debug(res)

        data = open(tmp_img, 'rb').read()

        self._finish(tmp_inp, tmp_out, tmp_img)
        if not data:
            return None
        return data
    #
    # Utils
    #
    def _can_convert(self):
        """ Check if pdftk is installed
        """
        return CAN_GENERATE_COVER_IMAGE

    def _finish(self, *paths):
        """ remove temporary files
        """
        for path in paths:
            try:
                os.remove(path)
            except Exception, err:
                logger.warn(err)
