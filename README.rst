=============
EEA Converter
=============
.. image:: http://ci.eionet.europa.eu/job/eea.converter-www/badge/icon
  :target: http://ci.eionet.europa.eu/job/eea.converter-www/lastBuild
.. image:: http://ci.eionet.europa.eu/job/eea.converter-plone4/badge/icon
  :target: http://ci.eionet.europa.eu/job/eea.converter-plone4/lastBuild
.. image:: http://ci.eionet.europa.eu/job/eea.converter-zope/badge/icon
  :target: http://ci.eionet.europa.eu/job/eea.converter-zope/lastBuild

Introduction
============
This package provides utilities to convert images and PDF files
using ImageMagick. Also, toghether with `eea.pdf`_
users can download HTML pages as PDFs *with custom cover and back cover support*

Installation
============

- Add eea.converter to your eggs section in your buildout and re-run buildout.
  You can download a sample buildout from
  https://github.com/collective/eea.converter/tree/master/buildouts/plone4

Getting started
===============

1. Try http://localhost:8080/Plone/front-page/download.pdf


Customize output PDF
====================

Cover
-----
Provide custom browser:page called *@@pdf.cover*::

  <browser:page
    for="my.package.interfaces.ICustomContent"
    name="pdf.cover"
    class=".app.pdfview.Cover"
    template="zpt/pdf.cover.pt"
    permission="zope2.View"
    />

Disclaimer
----------
First page after PDF Cover containing author details and copyrights.
Provide custom browser:page called *@@pdf.cover*::

  <browser:page
    for="my.package.interfaces.ICustomContent"
    name="pdf.disclaimer"
    class=".app.pdfview.Disclaimer"
    template="zpt/pdf.disclaimer.pt"
    permission="zope2.View"
    />

Body
----
Provide custom browser:page called *@@pdf.body*::

  <browser:page
    for="my.package.interfaces.ICustomContent"
    name="pdf.body"
    class=".app.pdfview.Body"
    template="zpt/pdf.body.pt"
    permission="zope2.View"
    />

Back Cover
----------
Provide custom browser:page called *@@pdf.cover.back*::

  <browser:page
    for="my.package.interfaces.ICustomContent"
    name="pdf.cover.back"
    class=".app.pdfview.BackCover"
    template="zpt/pdf.cover.back.pt"
    permission="zope2.View"
    />

Options
-------

For PDF cover you'll have to provide a named adapter like::

  <adapter
    name="pdf.cover"
    for=" my.package.interfaces.ICustomContent"
    provides="eea.converter.interfaces.IPDFOptionsMaker"
    factory=".adapters.CoverOptionsMaker" />

Same for PDF disclaimer::

  <adapter
    name="pdf.disclaimer"
    for=" my.package.interfaces.ICustomContent"
    provides="eea.converter.interfaces.IPDFOptionsMaker"
    factory=".adapters.DisclaimerOptionsMaker" />

Or for PDF back cover::

  <adapter
    name="pdf.cover.back"
    for=" my.package.interfaces.ICustomContent"
    provides="eea.converter.interfaces.IPDFOptionsMaker"
    factory=".adapters.BackCoverOptionsMaker" />

For PDF body you'll have to provide an unnamed adapter like::

  <adapter
    for=" my.package.interfaces.ICustomContent"
    provides="eea.converter.interfaces.IPDFOptionsMaker"
    factory=".adapters.OptionsMaker" />

Also add custom print.css for your needs. See more at `eea.pdf`_

Dependencies
============

.. note ::

  These are not hard dependencies. You can use all features of eea.converter or
  just the ones that you need.

* pdfinfo to parse pdf metadata (part of the xpdf package)::

    yum install xpdf (fedora)
    apt-get install xpdf (debian)

* pdftk to generate a cover image from a pdf file::

    yum install pdftk (fedora)
    apt-get install pdftk (debian)

* ImageMagick (6.3.7+)::

    yum install ImageMagick
    apt-get install imagemagick

* `eea.pdf`_


Source code
===========

Latest source code (Zope 2 compatible):
  - `Plone Collective on Github <https://github.com/collective/eea.converter>`_
  - `EEA on Github <https://github.com/eea/eea.converter>`_


Documentation
=============

See the **doc** directory in this package.


API Doc
=======

http://apidoc.eea.europa.eu/eea.converter-module.html

Copyright and license
=====================
The Initial Owner of the Original Code is European Environment Agency (EEA).
All Rights Reserved.

The EEA Exhibit (the Original Code) is free software;
you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later
version.

More details under docs/License.txt


Funding
=======

EEA_ - European Environment Agency (EU)

.. _EEA: http://www.eea.europa.eu/
.. _`plone.recipe.zope2instance`: http://pypi.python.org/pypi/plone.recipe.zope2instance
.. _`zc.buildout`: http://pypi.python.org/pypi/zc.buildout
.. _`eea.googlecharts`: http://eea.github.com/docs/eea.googlecharts
.. _`eea.pdf`: http://eea.github.com/docs/eea.pdf
