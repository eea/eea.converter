"""Common configuration constants
"""
import os
import logging
from zope.i18nmessageid import MessageFactory

logger = logging.getLogger('eea.converter')
EEAMessageFactory = MessageFactory('eea')
PROJECTNAME = 'eea.converter'


def TMPDIR():
    """ GET EEACONVERTER_TEMP from os env
    """
    path = os.environ.get('EEACONVERTER_TEMP')
    if not path:
        path = os.environ.get('CLIENT_HOME', '/tmp')
        path = os.path.join(path, 'tmp')
        os.environ['EEACONVERTER_TEMP'] = path
        logger.warn('Missing environment var EEACONVERTER_TEMP. Using %s', path)
    return path


def ASYNC():
    """ Asynchronous download
    """
    if os.environ.get('EEACONVERTER_ASYNC'):
        return True
    return False
