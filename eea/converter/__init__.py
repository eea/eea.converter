""" Converters
"""
import logging
from subprocess import Popen, PIPE, STDOUT
logger = logging.getLogger('eea.converter')

def can_convert_image():
    """ Check if pdftk is installed
    """
    # Test for ImageMagik
    process = Popen('convert --version', shell=True,
                    stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    res = process.stdout.read()
    if 'imagemagick' not in res.lower():
        logger.warn(
            ("ImageMagick NOT FOUND: "
             "Automatic generation of report's cover image is not supported."))
        return False
    return True

def can_update_pdf_metadata():
    """ Check if pdftk is installed
    """
    process = Popen('pdftk --version', shell=True,
                    stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    res = process.stdout.read()
    if 'handy tool' not in res.lower():
        logger.warn("pdftk NOT FOUND: PDF metadata syncronize is not supported")
        return False
    return True

CAN_UPDATE_PDF_METADATA = can_update_pdf_metadata()
CAN_CONVERT_IMAGE = can_convert_image()
CAN_GENERATE_COVER_IMAGE = CAN_UPDATE_PDF_METADATA and CAN_CONVERT_IMAGE
