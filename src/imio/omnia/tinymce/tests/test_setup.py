# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from imio.omnia.tinymce.testing import IMIO_OMNIA_TINYMCE_INTEGRATION_TESTING

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that imio.omnia.tinymce is properly installed."""

    layer = IMIO_OMNIA_TINYMCE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if imio.omnia.tinymce is installed."""
        self.assertTrue(self.installer.is_product_installed(
            'imio.omnia.tinymce'))

    def test_browserlayer(self):
        """Test that IImioOmniaTinyMCELayer is registered."""
        from imio.omnia.tinymce.interfaces import IImioOmniaTinyMCELayer
        from plone.browserlayer import utils
        self.assertIn(
            IImioOmniaTinyMCELayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = IMIO_OMNIA_TINYMCE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstall_product('imio.omnia.tinymce')
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if imio.omnia.tinymce is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed(
            'imio.omnia.tinymce'))

    def test_browserlayer_removed(self):
        """Test that IImioOmniaTinyMCELayer is removed."""
        from imio.omnia.tinymce.interfaces import IImioOmniaTinyMCELayer
        from plone.browserlayer import utils
        self.assertNotIn(IImioOmniaTinyMCELayer, utils.registered_layers())
