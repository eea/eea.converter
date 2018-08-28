""" Converters
"""
import logging
import os
import sys
from subprocess import Popen, PIPE, STDOUT

from eea.converter.config import TMPDIR

from zope.i18nmessageid import MessageFactory

MessageFactory = MessageFactory('eea')

logger = logging.getLogger('eea.converter')

CLOSE_FDS = not sys.platform.startswith('win')


def can_convert_svg():
    """ Check if rsvg-convert is installed
    """
    process = Popen('rsvg-convert --version', shell=True,
                    stdin=PIPE, stdout=PIPE, stderr=STDOUT,
                    close_fds=CLOSE_FDS)
    res = process.stdout.read()
    if 'version' not in res.lower():
        logger.warn(
            ("rsvg-convert NOT FOUND: "
             "ImageMagick will be used to export SVG to PNG images."))
        return False
    return True

def can_convert_image():
    """ Check if ImageMagick is installed
    """
    # Test for ImageMagik
    process = Popen('convert --version', shell=True,
                    stdin=PIPE, stdout=PIPE, stderr=STDOUT,
                    close_fds=CLOSE_FDS)
    res = process.stdout.read()
    if 'imagemagick' not in res.lower():
        logger.warn(
            ("ImageMagick NOT FOUND: "
             "Automatic generation of report's cover image is not supported."))
        return False
    return True

WK_COMMAND = os.environ.get('WKHTMLTOPDF_PATH')
if WK_COMMAND:
    logger.info('wkhtmltopdf found at  %s: ', WK_COMMAND)
else:
    WK_COMMAND = 'wkhtmltopdf'
    logger.warn("wkhtmltopdf path unknown, hope it's in the path")

CAN_CONVERT_SVG = can_convert_svg()
CAN_CONVERT_IMAGE = can_convert_image()


def initialize(context):
    """Initializer called when used as a Zope 2 product.
    """
    path = TMPDIR()
    if not path:
        raise AttributeError('Missing environment var EEACONVERTER_TEMP')
    elif not os.path.exists(path):
        os.makedirs(path)
