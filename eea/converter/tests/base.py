""" Base test cases
"""
from plone.testing import z2
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer

class EEAFixture(PloneSandboxLayer):
    """ Custom fixture
    """

    def setUpZope(self, app, configurationContext):
        """ Setup Zope
        """
        import eea.converter
        self.loadZCML(package=eea.converter)
        z2.installProduct(app, 'eea.converter')

    def tearDownZope(self, app):
        """ Uninstall Zope
        """
        z2.uninstallProduct(app, 'eea.converter')

EEAFIXTURE = EEAFixture()
FUNCTIONAL_TESTING = FunctionalTesting(bases=(EEAFIXTURE,),
            name='EEAConverter:Functional')
