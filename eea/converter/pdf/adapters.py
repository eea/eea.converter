""" PDF Adapters
"""
import logging
from zope.component.hooks import getSite
logger = logging.getLogger('eea.converter')

class OptionsMaker(object):
    """ PDF Converter for Archetypes
    """
    def __init__(self, context):
        self.context = context
        self._header = None
        self._footer = None

    @property
    def header(self):
        """ Safely get pdf.header
        """
        if not self._header:
            try:
                self.context.restrictedTraverse('@@pdf.header')
            except Exception, err:
                logger.exception(err)
                self._header = getSite().absolute_url() + '/pdf.header'
            else:
                self._header = self.context.absolute_url() + '/pdf.header'
        return self._header

    @property
    def footer(self):
        """ Safely get pdf.footer
        """
        if not self._footer:
            try:
                self.context.restrictedTraverse('@@pdf.footer')
            except Exception, err:
                logger.exception(err)
                self._footer = getSite().absolute_url() + '/pdf.footer'
            else:
                self._footer = self.context.absolute_url() + '/pdf.footer'
        return self._footer

    def overrideAll(self):
        """ Override all options
        """
        return True

    def getOptions(self):
        """ Custom options
        """
        return {
            # Header
            'header-html': self.header,
            'header-font-size': '9',
            'header-spacing': '5',
            'header-font-name': 'Verdana',

            # Footer
            'footer-html': self.footer,
            'footer-font-size': '9',
            'footer-font-name': 'Verdana',
            'footer-spacing': '5',

            # Document layout
            'page-size': 'A4',
            'margin-top': '32',
            'margin-bottom': '32',
            'margin-left': '20',
            'margin-right': '20',
            'page-offset': '2',
        }

class CoverOptionsMaker(object):
    """ PDF Converter for Cover
    """
    def __init__(self, context):
        self.context = context

    def overrideAll(self):
        """ Override all options
        """
        return True

    def getOptions(self):
        """ Custom options
        """

        return {
            'page-size': 'A4',
            'margin-top': '0',
            'margin-bottom': '0',
            'margin-left': '0',
            'margin-right': '0',
        }
