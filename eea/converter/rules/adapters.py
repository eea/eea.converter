""" Content-rules string substitution
"""
from plone.stringinterp.adapters import BaseSubstitution
from eea.converter.config import EEAMessageFactory as _

class DownloadTitle(BaseSubstitution):
    """ Download title substitution
    """
    category = _(u'Download')
    description = _(u'Download title')

    def safe_call(self):
        """ Safe call
        """
        return getattr(self.wrapper, 'title', '')

class DownloadEmail(BaseSubstitution):
    """ Download email substitution
    """
    category = _(u'Download')
    description = _(u'Download e-mail')

    def safe_call(self):
        """ Safe call
        """
        return getattr(self.wrapper, 'email', '')

class DownloadUrl(BaseSubstitution):
    """ Download email substitution
    """
    category = _(u'Download')
    description = _(u'Download URL')

    def safe_call(self):
        """ Safe call
        """
        return getattr(self.wrapper, 'fileurl', '')

class DownloadCameFromUrl(BaseSubstitution):
    """ Download email substitution
    """
    category = _(u'Download')
    description = _(u'Download came from URL')

    def safe_call(self):
        """ Safe call
        """
        return getattr(self.wrapper, 'url', '')

class DownloadError(BaseSubstitution):
    """ Download error
    """
    category = _(u'Download')
    description = _(u'Download error')

    def safe_call(self):
        """ Safe call
        """
        return getattr(self.wrapper, 'error', '')

class DownloadFromName(BaseSubstitution):
    """ Download from name
    """
    category = _(u'Download')
    description = _(u'Download from name')

    def safe_call(self):
        """ Safe call
        """
        return getattr(self.wrapper, 'from_name', '')

class DownloadFromEmail(BaseSubstitution):
    """ Download from name
    """
    category = _(u'Download')
    description = _(u'Download from email')

    def safe_call(self):
        """ Safe call
        """
        return getattr(self.wrapper, 'from_email', '')

class DownloadType(BaseSubstitution):
    """ Download from name
    """
    category = _(u'Download')
    description = _(u'Download type')

    def safe_call(self):
        """ Safe call
        """
        return getattr(self.wrapper, 'etype', 'pdf').upper()
