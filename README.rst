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
using `ImageMagick`_. It also provides a generic /download.pdf browser view that
allow your users to download Plone pages as PDF files with custom PDF cover,
disclaimer and back cover (requires `wkhtmltopdf`_ system-package
installed on your server).


Main features
=============
- Download Plone/Zope content as PDF files with custom PDF cover, table of contents, etc;
- Provide utilities to extract PDF cover as image (using `PyPDF2`_ and `ImageMagick`_);
- Provide utilities to extract metadata from PDF (using `PyPDF2`_);
- Provide utilities to update PDF metadata (using `PyPDF2`_).


Installation
============

- Make sure you have `wkhtmltopdf`_ 0.12.1+ installed or install it via `zc.buildout`_
- Make sure you have `ImageMagick`_ 6.3.7+ installed or install it via `zc.buildout`_
- Make sure you have an OS environment called EEACONVERTER_TEMP within your
  buildout if you have zope instances over more than one physical server.
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

Table of contents
-----------------
To enable Table of contents provide an empty browser:page called *@@pdf.toc*::

  <browser:page
    for="my.package.interfaces.ICustomContent"
    name="pdf.toc"
    template="zpt/pdf.toc.pt"
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

For PDF body you'll have to provide a named adapter like::

  <adapter
    name="pdf.body"
    for=" my.package.interfaces.ICustomContent"
    provides="eea.converter.interfaces.IPDFOptionsMaker"
    factory=".adapters.BodyOptionsMaker" />

For global PDF options provide an unamed adapter like::

  <adapter
    for=" my.package.interfaces.ICustomContent"
    provides="eea.converter.interfaces.IPDFOptionsMaker"
    factory=".adapters.OptionsMaker" />

Also add custom print.css for your needs. See more at `eea.pdf`_

Restrict access and async
=========================
In order to restrict access to /download.pdf you'll have to provide a
multi-adapter named pdf.support with a method called **can_download**
like::

  <browser:page
    name="pdf.support"
    for="zope.interface.Interface"
    class=".support.Support"
    permission="zope.Public"
    allowed_interface="eea.converter.interfaces.ISupport"
    />

Same for asynchronous download, define a method called **async**.
See default implementation within eea.converter.browser.app.support or add an
environment var called EEACONVERTER_ASYNC within your buildout.cfg::

  [instance]
  ...
  environment-vars =
    EEACONVERTER_ASYNC True


Content rules
=============
This package uses Plone Content-rules to notify users by email when an
asynchronous job is done. Thus 3 custom content-rules will be added within
Plone > Site Setup > Content-rules

.. warning ::

  As these content-rules are triggered by an asynchronous job, while
  you customize the email template for these content-rules,
  please **DO NOT USE OTHER** string substitutions **that the ones** that start
  with **$download_** as you'll break the download chain.
  Also if you disable these content-rules the users will never know when the
  file is ready and what is the link where they can download the output document.

Export succeeded
----------------
Notify the person who requested a PDF/ePub export that the document
successfully exported and provide a link to the downloadable file.

Export failed
-------------
Notify the person who requested a PDF/ePub export that the export failed.

Export failed (admin)
---------------------
Notify admin that there were issues while exporting PDF/ePub


Content rules email string substitution
=======================================
In order to be able to easily customize emails sent by this package the following
custom email template string substitutions can be made


${download_came_from_url}
-------------------------
The absolute URL of the Plone object which is downloaded as PDF/ePub

${download_email}
-----------------
Email address of the user that triggered the download as PDF/ePub action

${download_error}
-----------------
Error traceback when download as PDF/ePub job fails

${download_from_email}
----------------------
Site Admin email address customizable via Plone > Site Setup > Mail

${download_from_name}
---------------------
Site Admin name customizable via Plone > Site Setup > Mail

${download_title}
-----------------
Title of the Plone object which is downloaded as PDF/ePub

${download_url}
---------------
The absolute URL where the generated output PDF/ePub can be downloaded

${download_type}
----------------
Download type: PDF/ePub


Dependencies
============

.. note ::

  These are not hard dependencies. You can use all features of eea.converter or
  just the ones that you need.

.. _imagemagick:

* ImageMagick (6.3.7+)::

    yum install ImageMagick
    apt-get install imagemagick

.. _wkhtmltopdf:

* wkhtmltopdf (0.12.1+):

    `Download and install <http://wkhtmltopdf.org/downloads.html>`_

* `eea.pdf`_ (optional for advanced PDF export)
* `eea.epub`_ (optional for ePub export)


Source code
===========

Latest source code (Zope 2 compatible):
  - `Plone Collective on Github <https://github.com/collective/eea.converter>`_
  - `EEA on Github <https://github.com/eea/eea.converter>`_


Documentation
=============

See the **doc** directory in this package.


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
.. _`eea.pdf`: http://eea.github.com/docs/eea.pdf
.. _`eea.epub`: http://eea.github.com/docs/eea.epub
.. _`PyPDF2`: https://pypi.python.org/pypi/PyPDF2/1.25.1
