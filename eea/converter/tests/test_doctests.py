""" Doc tests
"""
import doctest
import unittest
from eea.converter.tests.base import FUNCTIONAL_TESTING
from plone.testing import layered

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def test_suite():
    """ Suite
    """
    suite = unittest.TestSuite()
    suite.addTests([
        layered(
            doctest.DocFileSuite(
                'docs/convert.txt',
                optionflags=OPTIONFLAGS,
                package='eea.converter'),
            layer=FUNCTIONAL_TESTING),
        layered(
            doctest.DocFileSuite(
                'docs/coverimage.txt',
                optionflags=OPTIONFLAGS,
                package='eea.converter'),
            layer=FUNCTIONAL_TESTING),
        layered(
            doctest.DocFileSuite(
                'docs/metaparser.txt',
                optionflags=OPTIONFLAGS,
                package='eea.converter'),
            layer=FUNCTIONAL_TESTING),
        layered(
            doctest.DocFileSuite(
                'docs/metaupdater.txt',
                optionflags=OPTIONFLAGS,
                package='eea.converter'),
            layer=FUNCTIONAL_TESTING),
        layered(
            doctest.DocFileSuite(
                'utils.py',
                optionflags=OPTIONFLAGS,
                package='eea.converter'),
            layer=FUNCTIONAL_TESTING),
    ])
    return suite
