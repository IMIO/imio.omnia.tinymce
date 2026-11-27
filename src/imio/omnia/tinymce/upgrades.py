# -*- coding: utf-8 -*-
"""GenericSetup upgrade steps."""

ENABLED_FEATURES_KEY = (
    "imio.omnia.tinymce.browser.controlpanel.IOmniaTinyMCESettings.enabled_features"
)


def upgrade_1001_to_1002(context):
    """Replace make-accessible by structure-text and simplify-text."""
    from plone.registry.interfaces import IRegistry
    from zope.component import getUtility

    registry = getUtility(IRegistry)
    record = registry.records.get(ENABLED_FEATURES_KEY)
    old_features = tuple(record.value or ()) if record is not None else ()

    # The registry stores its own copy of the field: re-import it so the
    # Choice accepts the new values (and no longer make-accessible).
    context.runImportStepFromProfile(
        "profile-imio.omnia.tinymce:default", "plone.app.registry"
    )

    if not old_features:
        return
    features = []
    for feature in old_features:
        if feature == "make-accessible":
            features.extend(("structure-text", "simplify-text"))
        else:
            features.append(feature)
    # Keep order, drop duplicates (a site may already list a successor).
    registry[ENABLED_FEATURES_KEY] = tuple(dict.fromkeys(features))
