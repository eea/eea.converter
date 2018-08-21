""" PDF Adapters
"""
import tempfile
from eea.converter.config import TMPDIR

class OptionsMaker(object):
    """ PDF Converter Global PDF options
    """
    def __init__(self, context):
        self.context = context
        self._timeout = None
        self._options = None
        self._cookies = None
        self._body = None
        self._margin = True
        self._outline = True

    @property
    def timeout(self):
        """ Kill process after timeout
        """
        if self._timeout is None:
            self._timeout = 60
        return self._timeout

    @property
    def body(self):
        """ PDF Body
        """
        if not self._body:
            self._body = ''
        return self._body

    @property
    def margin(self):
        """ PDF Margins
        """
        if not self._margin:
            return [
                '--margin-top', '0',
               '--margin-bottom', '0',
                '--margin-left', '0',
                '--margin-right', '0',
            ]
        return [
            '--margin-top', '32',
            '--margin-bottom', '32',
            '--margin-left', '20',
            '--margin-right', '20',
        ]

    @property
    def cookies(self):
        """ Allowed cookies
        """
        cookies = []
        if isinstance(self._cookies, dict):
            for name, value in self._cookies.items():
                cookies.extend(['--cookie', name, value])
        elif isinstance(self._cookies, (str, unicode)):
            cookies.extend(['--cookie-jar', self._cookies])
        return cookies

    @property
    def outline(self):
        """ Put an outline into the pdf
        """
        if not self._outline:
            return ['--no-outline']
        return ['--outline']

    @property
    def options(self):
        """ Salfely get global options
        """
        if self._options is None:
            self._options = [
                '--disable-smart-shrinking',
                '--page-size', 'A4',
                '--page-offset', '2',
                '--print-media-type',
                '--encoding', 'utf-8',
                '--quiet',
            ]
            self._options.extend(self.margin)
            self._options.extend(self.outline)
            self._options.extend(self.cookies)
        return self._options

    def __call__(self, **kwargs):
        margin = kwargs.get('margin', None)
        if margin is not None:
            self._margin = margin

        cookies = kwargs.get('cookies', None)
        if cookies is not None:
            self._cookies = cookies

        outline = kwargs.get('outline', None)
        if outline is not None:
            self._outline = outline

        return self.options

class BodyOptionsMaker(object):
    """ PDF Converter for Archetypes
    """
    def __init__(self, context):
        self.context = context
        self._header = None
        self._footer = None
        self._cookies = None
        self._toc = None
        self._toc_links = None
        self._body = None

    @property
    def cookies(self):
        """ Allowed cookies
        """
        cookies = []
        if isinstance(self._cookies, dict):
            for name, value in self._cookies.items():
                cookies.extend(['--cookie', name, value])
        return cookies

    @property
    def body(self):
        """ PDF body
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
        if self._header is None:
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
        if self._footer is None:
            try:
                self.context.restrictedTraverse('@@pdf.footer')
            except Exception:
                self._footer = ''
            else:
                self._footer = self.context.absolute_url() + '/pdf.footer'
        return self._footer

    @property
    def toc(self):
        """ Table of contents
        """
        if self._toc is None:
            try:
                body = self.context.restrictedTraverse('@@pdf.toc')
                body = body()
                if isinstance(body, unicode):
                    body = body.encode('utf-8')
            except Exception:
                self._toc = ''
            else:
                # self._toc = self.context.absolute_url() + '/pdf.toc'

                ## wkhtmltopdf doesn't support URLs for TOC xsl
                ## To be replaced with previous commented one when fixed by wk

                with tempfile.NamedTemporaryFile(
                        prefix='eea.converter.', suffix='.xsl',
                        dir=TMPDIR(), delete=False) as ofile:
                    ofile.write(body)
                    self._toc = ofile.name

                ## End patch
        return self._toc

    @property
    def toc_links(self):
        """ Enable table of contents links
        """
        if self._toc_links is None:
            self._toc_links = True
        return self._toc_links

    def __call__(self, **kwargs):
        options = []
        if not self.body:
            return options

        if self.toc:
            options.extend([
                'toc',
                '--xsl-style-sheet', self.toc,
            ])

            if self.toc_links is False:
                options.extend([
                    '--disable-toc-links',
                ])

        cookies = self.cookies
        if cookies:
            options.extend(cookies)

        options.extend([
            self.body,
            '--load-error-handling', 'ignore'
        ])

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
        self._body = None

    @property
    def body(self):
        """ Safely get pdf.cover
        """
        if not self._body:
            try:
                self.context.restrictedTraverse('@@pdf.cover')
            except Exception:
                self._body = ''
            else:
                self._body = self.context.absolute_url() + '/pdf.cover'
        return self._body

    def __call__(self, **kwargs):
        if self.body:
            return ['cover', self.body]
        return []

class BackCoverOptionsMaker(CoverOptionsMaker):
    """ PDF Converter for Back Cover
    """
    @property
    def body(self):
        """ Safely get pdf.cover
        """
        if not self._body:
            try:
                self.context.restrictedTraverse('@@pdf.cover.back')
            except Exception:
                self._body = ''
            else:
                self._body = self.context.absolute_url() + '/pdf.cover'
        return self._body

class DisclaimerOptionsMaker(CoverOptionsMaker):
    """ PDF Converter for Disclaimer
    """
    @property
    def body(self):
        """ Safely get pdf.disclaimer
        """
        if not self._body:
            try:
                self.context.restrictedTraverse('@@pdf.disclaimer')
            except Exception:
                self._body = ''
            else:
                self._body = self.context.absolute_url() + '/pdf.disclaimer'
        return self._body
