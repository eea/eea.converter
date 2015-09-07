""" Metadata parser
"""
import os
import re
import tempfile
import logging
import StringIO
from subprocess import Popen, PIPE, STDOUT
from types import InstanceType, StringType, UnicodeType, FileType
from zope import interface
from zope.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from eea.converter.interfaces import IPDFParser

logger = logging.getLogger('eea.reports.pdf')

class PDFParser(object):
    """ parses metadata from pdf files """

    interface.implements(IPDFParser)

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
        if not (isinstance(text, str) or isinstance(text, unicode)):
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

        # Fix effectiveDate
        if metadata.has_key('moddate'):
            metadata['effectiveDate'] = metadata.pop('moddate')
        elif metadata.has_key('modificationdate'):
            metadata['effectiveDate'] = metadata.pop('modificationdate')
        elif metadata.has_key('creationdate'):
            metadata['effectiveDate'] = metadata.pop('creationdate')

        # Fix description
        description = metadata.pop('subject', metadata.get('description', ''))
        if isinstance(description, tuple) or isinstance(description, list):
            description = ' '.join([y.strip() for y in description])
        if not description:
            description = ' '
        metadata['description'] = description

        # Fix subject
        keywords = metadata.pop('keywords', ())
        if keywords:
            keywords = self._split(keywords)
            metadata['subject'] = keywords
        else:
            metadata.pop('subject', '')

        return metadata

    def _parse(self, pdf, password=''):
        """ parses the given pdf file and returns a mapping of attributes """
        metadata = self._parsepdf(pdf, password)
        if not metadata:
            metadata = {}

        # Get plain/text metadata
        tmp_pdf = tempfile.mkstemp(suffix='.pdf')
        fd = open(tmp_pdf[1], 'w')
        fd.write(pdf)
        fd.close()
        statement = 'pdfinfo '
        if password:
            statement += '-opw %s ' % password
        statement += tmp_pdf[1]
        logger.debug('pdfinfo commandline: %s', statement)
        process = Popen(statement, shell=True,
                        stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        result = process.stdout.read()

        # cleanup the tempfile
        os.remove(tmp_pdf[1])

        # check for errors or encryption
        if result.startswith(
            'Error: No paper information available - using defaults'):
            # Irritating error if libpaper is not configured correctly.
            # For our case this is irrelevant
            pass
        elif result.startswith('Error'):
            error = result.split('\n')[0]
            logger.error("Error in pdfinfo conversion: %s", error)
            return metadata
        elif 'command not found' in result:
            return metadata

        crypt_patt = re.compile('Encrypted:.*?copy:no', re.I)
        mobj = crypt_patt.search(result, 1)
        if mobj is not None:
            error = "Error: PDF is encrypted"
            logger.error(error)
            return metadata

        result = result.replace('  ', ' ').replace('\r\n', '\n')
        res_list = result.splitlines()
        new_metadata = [[r.strip() for r in x.split(':', 1)]
                        for x in res_list]
        new_metadata = dict((x[0].lower(), x[1]) for x in new_metadata
                            if len(x) == 2)
        metadata.update(new_metadata)
        #
        # Fix some metadata
        #
        metadata = self._fix_metadata(metadata)
        return metadata

    def _parsepdf(self, pdf, owner_password='', user_password=''):
        """ parses the given pdf file and returns a mapping of attributes """

        # This will store the parsed metadata
        META_MAP = {}

        statement = "pdfinfo -meta"
        if owner_password != "":
            statement += ' -opw ' + owner_password
        if user_password != "":
            statement += ' -upw ' + user_password

        # pdfinfo needs to work on a file. Write the file and start pdfinfo
        tmp_pdf = tempfile.mkstemp(suffix='.pdf')
        fd = open(tmp_pdf[1], 'w')
        if isinstance(pdf, InstanceType) and pdf.__class__ == StringIO.StringIO:
            fd.write(pdf.getvalue())
        elif isinstance(pdf, StringType) or isinstance(pdf, UnicodeType):
            fd.write(pdf)
        elif isinstance(pdf, FileType):
            fd.write(str(pdf))
        else:
            raise ValueError, 'Cannot determine type of pdf variable'
        fd.close()

        statement += ' '+tmp_pdf[1]
        logger.debug('pdfinfo commandline: %s', statement)
        process = Popen(statement, shell=True,
                        stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

        # get the result
        result = process.stdout.read()
        logger.debug('metadata extracted by pdfinfo :\n---------\n%s ', result)

        # cleanup the tempfile
        os.remove(tmp_pdf[1])

        # check for errors or encryption
        if result.startswith(
            'Error: No paper information available - using defaults'):
            # Irritating error if libpaper is not configured correctly.
            # For our case this is irrelevant
            pass
        elif result.startswith('Error'):
            error = result.split('\n')[0]
            logger.error("Error in pdfinfo conversion: %s", error)
            return False

        crypt_patt = re.compile('Encrypted:.*?copy:no', re.I)
        mobj = crypt_patt.search(result, 1)
        if mobj is not None:
            error = "Error: PDF is encrypted"
            logger.error(error)
            return False

        # Everything seems fine, parse the metadata
        # Caution: do not use the metalist, it's not unicode!
        # Note that pdfinfo returns a ini style list and an xml version.
        METADATA = result.split('Metadata:')
        if len(METADATA) > 1:
            metaxml = METADATA[1]
        else:
            metaxml = ''

        # Get metadata out of the xml-part
        # If would be a good idea to make this generic
        # It even would be smart to use an xml parser here.
        patt_list = []
        patt_list.append(
            ('Keywords', "<pdf:Keywords>(.*?)</pdf:Keywords>"))
        patt_list.append(
            ('Keywords', "pdf:Keywords='(.*?)'"))
        patt_list.append(
            ('Language', "<pdf:Language>(.*?)</pdf:Language>"))
        patt_list.append(
            ('Language', "pdf:Language='(.*?)'"))
        patt_list.append(
            ('UUID', "xapMM:DocumentID='uuid:(.*?)'"))
        patt_list.append(
            ('UUID', 'rdf:about="uuid:(.*?)"'))
        patt_list.append(
            ('CreationDate', "xap:CreateDate='(.*?)'"))
        patt_list.append(
            ('CreationDate', "<xap:CreateDate>(.*?)</xap:CreateDate>"))
        patt_list.append(
            ('ModificationDate', "xap:ModifyDate='(.*?)'"))
        patt_list.append(
            ('ModificationDate', "<xap:ModifyDate>(.*?)</xap:ModifyDate>"))
        patt_list.append(
            ('MetadataDate', "xap:MetadataDate='(.*?)'"))
        patt_list.append(
            ('MetadataDate', "<xap:MetadataDate>(.*?)</xap:MetadataDate>"))
        patt_list.append(
            ('Rights Webstatement',
             "<xapRights:WebStatement>(.*?)</xapRights:WebStatement>"))
        patt_list.append(
            ('Producer', "<pdf:Producer>(.*?)</pdf:Producer>"))
        patt_list.append(
            ('CreatorTool', "<xap:CreatorTool>(.*?)</xap:CreatorTool>"))
        patt_list.append(
            ('Title', "<dc:title>(.*?)</dc:title>"))
        patt_list.append(
            ('Description', "<dc:description>(.*?)</dc:description>"))
        patt_list.append(
            ('Rights', "<dc:rights>(.*?)</dc:rights>"))
        patt_list.append(
            ('Format', "<dc:format>(.*?)</dc:format>"))
        patt_list.append(
            ('Creator', "<dc:creator>(.*?)</dc:creator>"))
        patt_list.append(
            ('OPOCE', "pdfx:OPOCE='(.*?)'"))
        patt_list.append(
            ('OPOCE', "<pdfx:OPOCE>(.*?)</pdfx:OPOCE>"))

        for patt in patt_list:
            pobj = re.compile(patt[1], re.I | re.S)
            mobj = pobj.search(metaxml, 1)
            if mobj is not None:
                value = re.sub('<.*?>', '', mobj.group(1)).strip()
                # acrobat separates keywords with a semicolon.
                # There is no datatyping
                # so we assume it is a list if a semicolon appears.
                if ";" in value:
                    kw = value.split(";")
                    value = tuple([x.strip() for x in kw])

                META_MAP[patt[0].strip().lower()] = value
            else:
                logger.debug("No matches for %s", str(patt[1]))


        # Get the user-defined meta-data
        add_patt = re.compile("pdfx:(.*?)='(.*?)'", re.I|re.S)

        for name, value in add_patt.findall(metaxml):
            # acrobat separates keywords with a semicolon.
            # There is no datatyping
            # so we assume it is a list if a semicolon appears.
            if ";" in value:
                kw = value.split(";")
                value = tuple([y.strip() for y in kw])
            META_MAP[name.strip().lower()] = value

        # And another format
        add_patt = re.compile("pdfx:(.*?)>(.*?)</pdfx:", re.I|re.S)
        for name, value in add_patt.findall(metaxml):
            # acrobat separates keywords with a semicolon.
            # There is no datatyping
            # so we assume it is a list if a semicolon appears.
            if ";" in value:
                kw = value.split(";")
                value = tuple([z.strip() for z in kw])
            META_MAP[name.strip().lower()] = value


        # If the language is given in the filename extension,
        # we consider that as
        # most explicit

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
        langs = portal_languages.getSupportedLanguages()

        langbyfileid = findAbbrev(filename)
        if langbyfileid in langs:
            return langbyfileid

        return ''
