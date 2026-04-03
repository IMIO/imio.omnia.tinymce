# -*- coding: utf-8 -*-
from collective.z3cform.datagridfield.blockdatagridfield import BlockDataGridFieldFactory
from imio.omnia.core.browser.controlpanel import OmniaCoreControlPanelFormWrapper
from imio.omnia.tinymce import _
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.autoform import directives
from plone.z3cform import layout
from zope import schema
from zope.interface import Interface


class IOmniaTinyMCESettings(Interface):
    directives.widget(omnia_endpoints=BlockDataGridFieldFactory)

    enabled_features = schema.Tuple(
        title=_("Enabled features"),
        description=_("Restrict to a subset of features. Leave empty for all features except generate."),
        value_type=schema.Choice(
            values=[
                "generate",
                "expand-text",
                "improve-text",
                "reduce-text",
                "correct-text",
                "make-accessible",
                "translate-text",
            ],
        ),
        required=False,
        missing_value=(),
        default=("expand-text", "improve-text", "reduce-text", "correct-text", "make-accessible", "translate-text"),
    )
    show_toolbar = schema.Bool(
        title=_("Show toolbar button"),
        required=False,
        default=True,
    )
    show_context_menu = schema.Bool(
        title=_("Show context menu"),
        required=False,
        default=True,
    )
    enable_shortcuts = schema.Bool(
        title=_("Enable keyboard shortcuts"),
        required=False,
        default=True,
    )

    translate_languages = schema.Tuple(
        title=_("Translation languages"),
        description=_("Language codes available for translation."),
        value_type=schema.Choice(
            values=[
                "fr",
                "nl",
                "de",
                "en",
                "es",
                "it"
            ],
        ),
        required=False,
        missing_value=(),
        default=("fr", "nl", "de", "en"),
    )
    default_translate_language = schema.TextLine(
        title=_("Default translation language"),
        required=False,
        default="fr",
    )

    floating_panel_mode = schema.Choice(
        title=_("Floating panel mode"),
        description=_("Display mode: inline near selection or centred with blur overlay."),
        values=["inline", "blur"],
        required=False,
        default="inline",
    )

    floating_panel_width = schema.TextLine(
        title=_("Floating panel width"),
        description=_("Width in pixels (e.g. 500) or 'full' for full viewport width."),
        required=False,
        default="500",
    )


class OmniaTinyMCEControlPanelForm(RegistryEditForm):
    label = _("TinyMCE Omnia settings")
    schema = IOmniaTinyMCESettings


OmniaTinyMCEControlPanelView = layout.wrap_form(OmniaTinyMCEControlPanelForm, OmniaCoreControlPanelFormWrapper)
