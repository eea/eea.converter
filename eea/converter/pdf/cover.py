""" Cover image
"""
import os
import tempfile
import logging
from subprocess import Popen, PIPE, STDOUT

from zope import interface
from eea.converter.interfaces import IPDFCoverImage
from PyPDF2 import PdfFileReader, PdfFileWriter
logger = logging.getLogger('eea.converter')


class PDFCoverImage(object):
    """ Generate pdf cover image using ImageMagick
    """
    interface.implements(IPDFCoverImage)

    #
    # Public interface
    #
    def generate(self, pdf, width=210, height=297, img='.gif'):
        """ Safely generate image. See interface for more details.
        """
        image = None
        try:
            image = self._generate(pdf, width, height, img='.gif')
        except RuntimeError, err:
            logger.debug('Could not generate pdf cover image: %s', err)
        except Exception, err:
            logger.warn('Could not generate pdf cover image: %s', err)
        return image

    def _generate(self, pdf, width=210, height=297, img='.gif'):
        """ generate image from given pdf
        """
        tmp_inp = tempfile.mktemp(suffix='.pdf')
        tmp_img = tempfile.mktemp(suffix=img)

        cover = PdfFileReader(pdf).getPage(0)
        out = PdfFileWriter()
        out.addPage(cover)
        with open(tmp_inp, 'wb') as sock:
            out.write(sock)

        # Run image magick convert
        # add -flatten option to fix #28943. It's prevent transparence cover
        # image
        cmd = "convert -flatten -colorspace CMYK %s[0] -resize %sx%s %s" % (
            tmp_inp, width, height, tmp_img
        )
        process = Popen(cmd, shell=True,
                        stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        res = process.stdout.read()
        if res:
            logger.debug(res)

        data = open(tmp_img, 'rb').read()

        self._finish(tmp_inp, tmp_img)
        if not data:
            return None
        return data

    #
    # Cleanup
    #
    def _finish(self, *paths):
        """ remove temporary files
        """
        for path in paths:
            try:
                os.remove(path)
            except Exception, err:
                logger.warn(err)
