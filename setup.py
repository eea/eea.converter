""" Installer
"""
import os
from os.path import join
from setuptools import setup, find_packages

NAME = 'eea.converter'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(join(*PATH)).read().strip()

setup(name=NAME,
      version=VERSION,
      description=("SVG, PNG, PDF converters using external "
                   "tools as ImageMagick"),
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='eea converter imagemagick pdftk utility',
      author='Alin Voinea, European Environment Agency',
      author_email="webadmin@eea.europa.eu",
      url='http://svn.eionet.europa.eu',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['eea'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      extras_require={
          'test': ['plone.app.testing',]
      },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
