Introduction
============
This package provides utilities to convert images and PDF files
using ImageMagick.


Installation
------------

The easiest way to get eea.converter support in Plone 4 using this package is to
work with installations based on `zc.buildout`_.  Other types of installations
should also be possible, but might turn out to be somewhat tricky.

To get started you will simply need to add the package to your "eggs" and
"zcml" sections, run buildout, restart your Plone instance and install the
"eea.converter" package using the quick-installer or via the "Add-on
Products" section in "Site Setup".

  .. _`zc.buildout`: http://pypi.python.org/pypi/zc.buildout/

You can download a sample buildout at:

  http://svn.eionet.europa.eu/repositories/Zope/trunk/eea.converter/buildouts/plone4/


Dependencies
------------

  * pdfinfo to parse pdf metadata (part of the xpdf package)::

      yum install xpdf (fedora)
      apt-get install xpdf (debian)

  * pdftk to generate a cover image from a pdf file::

      yum install pdftk (fedora)
      apt-get install pdftk (debian)

  * ImageMagick (6.3.7+)::

      yum install ImageMagick
      apt-get install imagemagick


Documentation
-------------

  See the **doc** directory in this package.


API Doc
-------

  http://apidoc.eea.europa.eu/eea.converter-module.html

Authors
-------

  - "European Environment Agency", webadmin at eea europa eu


Copyright and license
---------------------

The Initial Owner of the Original Code is European Environment Agency (EEA).
All Rights Reserved.

The EEA Daviz (the Original Code) is free software;
you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later
version.

More details under docs/License.txt


Funding
-------

  EEA_ - European Enviroment Agency (EU)

.. _EEA: http://www.eea.europa.eu/
