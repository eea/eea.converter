""" Download as PDF
"""
import os
import logging
from subprocess import Popen, PIPE, STDOUT

from Products.Five.browser import BrowserView
from zope.component import queryMultiAdapter, queryAdapter
from eea.converter.interfaces import IPDFOptionsMaker

logger = logging.getLogger('eea.converter')

PDF = [
    # Global PDF options
    '',

    # Cover
    'pdf.cover',

    # Disclaimer
    'pdf.disclaimer',

    # Table of contents
    'pdf.toc',

    # Body
    'pdf.body',

    # Back cover
    'pdf.cover.back'
]

class Pdf(BrowserView):
    """ Download as PDF using @@pdf.cover and @@pdf.body browser views
    """
    def options(self, section=u''):
        """ Get options for given section
        """
        options = queryAdapter(
            self.context, IPDFOptionsMaker, name=section,
            default=lambda: [])

        return options()

    def make_pdf(self):
        """ Override pdf converter
        """
        options = []
        # Cover options
        for section in PDF:
            options.extend(self.options(section))

        return options

    def __call__(self, **kwargs):
        # Cheat condition @@plone_context_state/is_view_template
        self.request['ACTUAL_URL'] = self.context.absolute_url()
        return self.make_pdf()
