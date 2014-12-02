"""Common configuration constants
"""
import os

PROJECTNAME = 'eea.converter'

def TMPDIR():
    """ GET EEACONVERTER_TEMP from os env
    """
    return os.environ.get('EEACONVERTER_TEMP')

from zope.i18nmessageid import MessageFactory
EEAMessageFactory = MessageFactory('eea')
