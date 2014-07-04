""" PDF Adapters
"""
class OptionsMaker(object):
    """ PDF Converter Global PDF options
    """
    def __init__(self, context):
        self.context = context

    def __call__(self, **kwargs):
        return [
             '--page-size', 'A4',
            '--margin-top', '32',
             '--margin-bottom', '32',
             '--margin-left', '20',
             '--page-offset', '2',
             '--margin-right', '20',
             '--print-media-type'
        ]

class BodyOptionsMaker(object):
    """ PDF Converter for Archetypes
    """
    def __init__(self, context):
        self.context = context
        self._header = None
        self._footer = None
        self._body = None

    @property
    def body(self):
        """
        :return: pdf.body
        """
        if not self._body:
            try:
                self.context.restrictedTraverse('@@pdf.body')
            except Exception:
                self._body = ''
            else:
                self._body = self.context.absolute_url() + '/pdf.body'
        return self._body

    @property
    def header(self):
        """ Safely get pdf.header
        """
        if not self._header:
            try:
                self.context.restrictedTraverse('@@pdf.header')
            except Exception:
                self._header = ''
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
            except Exception:
                self._footer = ''
            else:
                self._footer = self.context.absolute_url() + '/pdf.footer'
        return self._footer

    def __call__(self, **kwargs):
        options = []
        if not self.body:
            return options

        options.extend([self.body])

        if self.header:
            options.extend([
                '--header-html', self.header,
                '--header-font-size', '9',
                '--header-spacing', '5',
                '--header-font-name', 'Verdana',
            ])

        if self.footer:
            options.extend([
                '--footer-html', self.footer,
                '--footer-font-size', '9',
                '--footer-font-name', 'Verdana',
                '--footer-spacing', '5',
            ])

        return options

class CoverOptionsMaker(object):
    """ PDF Converter for Cover
    """
    def __init__(self, context):
        self.context = context
        self._cover = None

    @property
    def cover(self):
        """ Safely get pdf.cover
        """
        if not self._cover:
            try:
                self.context.restrictedTraverse('@@pdf.cover')
            except Exception:
                self._cover = ''
            else:
                self._cover = self.context.absolute_url() + '/pdf.cover'
        return self._cover

    def __call__(self, **kwargs):
        if self.cover:
            return ['cover', self.cover]
        return []

class BackCoverOptionsMaker(CoverOptionsMaker):
    """ PDF Converter for Back Cover
    """
    @property
    def cover(self):
        """ Safely get pdf.cover
        """
        if not self._cover:
            try:
                self.context.restrictedTraverse('@@pdf.cover.back')
            except Exception:
                self._cover = ''
            else:
                self._cover = self.context.absolute_url() + '/pdf.cover.back'
        return self._cover

    def __call__(self, **kwargs):
        if self.cover:
            return [self.cover]
        return []

class TocOptionsMaker(object):
    """ PDF Table of contents
    """
    def __init__(self, context):
        self.context = context
        self._toc = None

    @property
    def toc(self):
        """ Table of contents
        """
        if not self._toc:
            try:
                self.context.restrictedTraverse('@@pdf.toc')
            except Exception:
                self._toc = ''
            else:
                self._toc = self.context.absolute_url() + '/pdf.toc'
        return self._toc

    def __call__(self, **kwargs):
        if self.toc:
            return ['toc']
        return []

class DisclaimerOptionsMaker(object):
    """ PDF Converter for Disclaimer
    """
    def __init__(self, context):
        self.context = context
        self._disclaimer = None

    @property
    def disclaimer(self):
        """ Safely get pdf.disclaimer
        """
        if not self._disclaimer:
            try:
                self.context.restrictedTraverse('@@pdf.disclaimer')
            except Exception:
                self._disclaimer = ''
            else:
                self._disclaimer = (
                    self.context.absolute_url() + '/pdf.disclaimer')
        return self._disclaimer

    def __call__(self, **kwargs):
        if self.disclaimer:
            return [self.disclaimer]
        return []
