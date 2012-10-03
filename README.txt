=============
EEA Converter
=============
This package provides utilities to convert images and PDF files
using ImageMagick.

.. note ::

  This add-on doesn't do anything by itself. It needs to be integrated by a
  developer within your own products. For reference you can check
  the `eea.googlecharts`_ package.


Installation
============

zc.buildout
-----------
If you are using `zc.buildout`_ and the `plone.recipe.zope2instance`_
recipe to manage your project, you can do this:

* Update your buildout.cfg file:

  * Add ``eea.converter`` to the list of eggs to install
  * Tell the `plone.recipe.zope2instance`_ recipe to install a ZCML slug

  ::

    [instance]
    ...
    eggs =
      ...
      eea.converter

    zcml =
      ...
      eea.converter

* Re-run buildout, e.g. with::

  $ ./bin/buildout

You can skip the ZCML slug if you are going to explicitly include the package
from another package's configure.zcml file.


Dependencies
============

  * pdfinfo to parse pdf metadata (part of the xpdf package)::

      yum install xpdf (fedora)
      apt-get install xpdf (debian)

  * pdftk to generate a cover image from a pdf file::

      yum install pdftk (fedora)
      apt-get install pdftk (debian)

  * ImageMagick (6.3.7+)::

      yum install ImageMagick
      apt-get install imagemagick


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