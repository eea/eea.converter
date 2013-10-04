""" Base test cases
"""
from plone.testing import z2
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
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

    def setUpPloneSite(self, portal):
        """ Setup Plone
        """
        # Login as manager
        setRoles(portal, TEST_USER_ID, ['Manager'])

        # Create testing environment
        portal.invokeFactory("Folder", "sandbox", title="Sandbox")
        portal['sandbox'].invokeFactory('Document', 'doc', title='Doc')

        portal.invokeFactory("Folder", "sandbox-1", title="Sandbox 1")
        portal.invokeFactory("Folder", "sandbox-2", title="Sandbox 2")


EEAFIXTURE = EEAFixture()
FUNCTIONAL_TESTING = FunctionalTesting(bases=(EEAFIXTURE,),
            name='EEAConverter:Functional')
