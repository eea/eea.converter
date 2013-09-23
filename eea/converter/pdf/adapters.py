""" PDF Adapters
"""
class OptionsMaker(object):
    """ PDF Converter for Archetypes
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
            'header-right': self.context.title_or_id(),
            'header-line': 1,
            'header-spacing': '5',
            'footer-left': '[page]' ,
            'footer-right': '[subsection]',
            'footer-line': 1,
            'footer-spacing': '5',
            'page-size': 'A4',
            'margin-top': '20',
            'margin-bottom': '20',
            'margin-left': '20',
            'margin-right': '20',
            'page-offset': '3',
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
            'cover': self.context.absolute_url() + '/pdf.cover',
            'page-size': 'A4',
            'margin-top': '0',
            'margin-bottom': '0',
            'margin-left': '0',
            'margin-right': '0',
        }
