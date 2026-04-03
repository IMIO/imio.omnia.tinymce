# -*- coding: utf-8 -*-
import json

from plone import api
from plone.app.layout.viewlets.common import ViewletBase
from plone.protect.authenticator import createToken


class OmniaConfigViewlet(ViewletBase):
    """Inject omnia_* TinyMCE options from the Plone registry into the page."""

    def get_config(self):
        tmce_prefix = "imio.omnia.tinymce.browser.controlpanel.IOmniaTinyMCESettings"

        def _get(key, default=None):
            try:
                return api.portal.get_registry_record(key)
            except (KeyError, api.exc.InvalidParameterError):
                return default

        config = {}

        # Point to the local proxy view instead of the external API.
        # Credentials (application, municipality) stay server-side.
        # We need the context path here so the proxy view can deduce the context safely.
        config["omnia_base_url"] = f"{self.context.absolute_url()}/@@omnia-api"

        config["omnia_auth_token"] = createToken()

        # From IOmniaTinyMCESettings
        enabled = _get(f"{tmce_prefix}.enabled_features")
        if enabled is not None:
            config["omnia_enabled_features"] = list(enabled)
        config["omnia_toolbar"] = _get(f"{tmce_prefix}.show_toolbar", True)
        config["omnia_context_menu"] = _get(f"{tmce_prefix}.show_context_menu", True)
        config["omnia_shortcuts"] = _get(f"{tmce_prefix}.enable_shortcuts", True)

        translate_langs = _get(f"{tmce_prefix}.translate_languages")
        if translate_langs is not None:
            config["omnia_translate_languages"] = list(translate_langs)
        default_lang = _get(f"{tmce_prefix}.default_translate_language", "fr")
        if default_lang:
            config["omnia_default_translate_language"] = default_lang

        panel_mode = _get(f"{tmce_prefix}.floating_panel_mode", "inline")
        if panel_mode:
            config["omnia_floating_panel_mode"] = panel_mode
        panel_width = _get(f"{tmce_prefix}.floating_panel_width", "500")
        if panel_width:
            config["omnia_floating_panel_width"] = (
                int(panel_width) if panel_width.isdigit() else panel_width
            )

        return config

    def config_json(self):
        return json.dumps(self.get_config())
