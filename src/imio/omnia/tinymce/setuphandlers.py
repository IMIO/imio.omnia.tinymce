# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "imio.omnia.tinymce:uninstall",
        ]

    def getNonInstallableProducts(self):
        """Hide the upgrades package from site-creation and quickinstaller."""
        return ["imio.omnia.tinymce.upgrades"]


def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.


def uninstall(context):
    """Uninstall script"""
    from plone.registry.interfaces import IRegistry
    from zope.component import getUtility

    registry = getUtility(IRegistry)

    # Remove omnia from custom_plugins
    key = "plone.custom_plugins"
    current = list(registry.get(key, []))
    registry[key] = [p for p in current if not p.startswith("omnia|")]

    # Remove omnia from custom_buttons
    key = "plone.custom_buttons"
    current = list(registry.get(key, []))
    registry[key] = [p for p in current if p != "omnia"]

    # Disable CSS bundle
    bundle_key = "plone.bundles/omnia-tinymce.enabled"
    if bundle_key in registry.records:
        registry[bundle_key] = False
