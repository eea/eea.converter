""" Metadata parser
"""
import logging
from PyPDF2 import PdfFileReader
from PyPDF2.generic import TextStringObject
from zope import interface
from zope.component.hooks import getSite
from eea.converter.interfaces import IPDFMetadataParser
try:
    from Products.CMFCore.utils import getToolByName
except ImportError:
    def getToolByName(**kwargs):
        """ Fallback if CMFCore not present
        """
        return None

logger = logging.getLogger('eea.converter')

class PDFParser(object):
    """ parses metadata from pdf files """

    interface.implements(IPDFMetadataParser)

    def parse(self, pdf, password=''):
        """ Safely parses the given pdf file and returns a mapping of attributes
        """
        try:
            metadata = self._parse(pdf, password)
        except Exception, err:
            logger.warn('Could not parse pdf metadata: %s', err)
            return {}
        else:
            return metadata

    def _split(self, text):
        """ Split text
        """
        if not isinstance(text, (str, unicode)):
            return text

        if text.find(';') != -1:
            return [x.strip() for x in text.split(';') if x.strip()]
        return [y.strip() for y in text.split(',') if y.strip()]

    def _fix_metadata(self, metadata):
        """ Update metadata dict
        """
        # Fix authors
        if metadata.has_key('author'):
            metadata['creators'] = self._split(metadata.pop('author', ''))
        if metadata.has_key('creator'):
            creator = self._split(metadata.pop('creator', ''))
            metadata.setdefault('creators', [])
            metadata['creators'].extend([
                x for x in creator if x not in metadata['creators']])


        # Fix description
        description = metadata.pop('subject', metadata.get('description', ''))
        if isinstance(description, (list, tuple)):
            description = u' '.join([y.strip() for y in description])

        if isinstance(description, TextStringObject):
            try:
                metadata['description'] = u"%s" % description
            except Exception, err:
                logger.exception(err)
                metadata['description'] = u''

        # Fix subject
        keywords = metadata.pop('keywords', ())
        if keywords:
            keywords = self._split(keywords)
            metadata['subject'] = keywords
        else:
            metadata.pop('subject', '')

        return metadata

    def _parse(self, pdf, password='', **kwargs):
        """ parses the given pdf file and returns a mapping of attributes """
        metadata = self._parsepdf(pdf, password)
        if not metadata:
            metadata = {}

        opdf = PdfFileReader(pdf)
        if password:
            opdf.decrypt(password)

        info = opdf.getDocumentInfo()

        new_metadata = dict(
            (key.strip('/').lower(), val) for key, val in info.items()
        )

        metadata.update(new_metadata)
        #
        # Fix some metadata
        #
        metadata = self._fix_metadata(metadata)
        return metadata

    def _parsepdf(self, pdf, password='', **kwargs):
        """ parses the given pdf file and returns a mapping of attributes """

        # This will store the parsed metadata
        META_MAP = {}

        opdf = PdfFileReader(pdf)

        if password != "":
            opdf.decrypt(password)

        metadata = opdf.getXmpMetadata()

        if getattr(metadata, 'pdf_keywords', None):
            META_MAP['keywords'] = metadata.pdf_keywords
        if getattr(metadata, 'dc_language', None):
            META_MAP['language'] = metadata.dc_language
        if getattr(metadata, 'dc_identifier', None):
            META_MAP['uuid'] = metadata.dc_identifier
        if getattr(metadata, 'xmpmm_documentId', None):
            META_MAP['uuid'] = metadata.xmpmm_documentId
        if getattr(metadata, 'xmpmm_instanceId', None):
            META_MAP['uuid'] = metadata.xmpmm_instanceId
        if getattr(metadata, 'xmp_createDate', None):
            META_MAP['creationdate'] = metadata.xmp_createDate
        if getattr(metadata, 'xmp_modifyDate', None):
            META_MAP['modificationdate'] = metadata.xmp_modifyDate
        if getattr(metadata, 'xmp_metadataDate', None):
            META_MAP['metadatadate'] = metadata.xmp_metadataDate
        if getattr(metadata, 'dc_rights', None):
            META_MAP['rights webstatement'] = metadata.dc_rights
        if getattr(metadata, 'pdf_producer', None):
            META_MAP['producer'] = metadata.pdf_producer
        if getattr(metadata, 'xmp_creatorTool', None):
            META_MAP['creatortool'] = metadata.xmp_creatorTool
        if getattr(metadata, 'dc_title', None):
            META_MAP['title'] = metadata.dc_title
        if getattr(metadata, 'dc_description', None):
            META_MAP['description'] = metadata.dc_description
        if getattr(metadata, 'dc_rights', None):
            META_MAP['rights'] = metadata.dc_rights
        if getattr(metadata, 'dc_format', None):
            META_MAP['format'] = metadata.dc_format
        if getattr(metadata, 'dc_creator', None):
            META_MAP['creator'] = metadata.dc_creator

        if getattr(metadata, 'custom_properties', None):
            META_MAP.update(metadata.custom_properties)

        l = self._guessLanguage(pdf)
        if l and not META_MAP.has_key('language'):
            META_MAP['language'] = l

        # Finally we'll do some plone specific rewritings
        # It would be smart to hook some kind of adapter
        # here so that one can define his own rewritings
        if META_MAP.has_key('keywords'):
            META_MAP['subject_keywords'] = list(META_MAP['keywords'])

        return META_MAP


    def _guessLanguage(self, pdffile):
        """
        try to find a language abbreviation in the string
        acceptable is a two letter language abbreviation at the
        start of the string followed by an _
        or at the end of the string prefixed by an _ just before the extension
        """
        if hasattr(pdffile, 'filename'):
            filename = pdffile.filename
        elif hasattr(pdffile, 'id'):
            filename = pdffile.id
        elif hasattr(pdffile, 'getId'):
            filename = pdffile.getId
        else:
            return None

        if callable(filename):
            filename = filename()

        def findAbbrev(fid):
            """ Find abbreviation
            """
            if len(fid) > 3 and fid[2] in ['_', '-']:
                lang = fid[0:2].lower()
                if lang in langs:
                    return lang
            if len(fid) > 3 and '.' in fid:
                elems = fid.split('.')
                filename = ".".join(elems[:-1])
                if len(filename) > 3 and filename[-3] in ['_', '-']:
                    lang = filename[-2:].strip()
                    if lang in langs:
                        return lang
                elif len(filename) == 2:
                    lang = filename
                    if lang in langs:
                        return lang


        site = getSite()
        portal_languages = getToolByName(site, 'portal_languages')

        getSupportedLanguages = getattr(
            portal_languages, 'getSupportedLanguages', lambda: {})
        langs = getSupportedLanguages()

        langbyfileid = findAbbrev(filename)
        if langbyfileid in langs:
            return langbyfileid

        return ''
