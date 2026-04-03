# -*- coding: utf-8 -*-
"""Tests for TinyMCE config viewlet generation."""
import json
import unittest
from unittest.mock import patch

from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from imio.omnia.tinymce.testing import IMIO_OMNIA_TINYMCE_INTEGRATION_TESTING


class TestOmniaConfigViewlet(unittest.TestCase):
    layer = IMIO_OMNIA_TINYMCE_INTEGRATION_TESTING

    PREFIX = "imio.omnia.tinymce.browser.controlpanel.IOmniaTinyMCESettings"

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def _make_viewlet(self):
        from imio.omnia.tinymce.browser.viewlets import OmniaConfigViewlet

        return OmniaConfigViewlet(self.portal, self.request, None, None)

    @patch("imio.omnia.tinymce.browser.viewlets.createToken")
    def test_get_config_uses_defaults(self, mock_token):
        mock_token.return_value = "csrf-token"

        config = self._make_viewlet().get_config()

        self.assertEqual(
            config["omnia_base_url"], f"{self.portal.absolute_url()}/@@omnia-api"
        )
        self.assertEqual(config["omnia_auth_token"], "csrf-token")
        self.assertEqual(
            config["omnia_enabled_features"],
            [
                "expand-text",
                "improve-text",
                "reduce-text",
                "correct-text",
                "make-accessible",
                "translate-text",
            ],
        )
        self.assertTrue(config["omnia_toolbar"])
        self.assertTrue(config["omnia_context_menu"])
        self.assertTrue(config["omnia_shortcuts"])
        self.assertEqual(
            config["omnia_translate_languages"], ["fr", "nl", "de", "en"]
        )
        self.assertEqual(config["omnia_default_translate_language"], "fr")
        self.assertEqual(config["omnia_floating_panel_mode"], "inline")
        self.assertEqual(config["omnia_floating_panel_width"], 500)

    @patch("imio.omnia.tinymce.browser.viewlets.createToken")
    def test_get_config_preserves_custom_registry_values(self, mock_token):
        mock_token.return_value = "csrf-token"
        api.portal.set_registry_record(
            f"{self.PREFIX}.enabled_features", ("generate", "translate-text")
        )
        api.portal.set_registry_record(f"{self.PREFIX}.show_toolbar", False)
        api.portal.set_registry_record(f"{self.PREFIX}.show_context_menu", False)
        api.portal.set_registry_record(f"{self.PREFIX}.enable_shortcuts", False)
        api.portal.set_registry_record(
            f"{self.PREFIX}.translate_languages", ("en", "es")
        )
        api.portal.set_registry_record(
            f"{self.PREFIX}.default_translate_language", "es"
        )
        api.portal.set_registry_record(f"{self.PREFIX}.floating_panel_mode", "blur")
        api.portal.set_registry_record(
            f"{self.PREFIX}.floating_panel_width", "full"
        )

        config = self._make_viewlet().get_config()

        self.assertEqual(
            config["omnia_enabled_features"], ["generate", "translate-text"]
        )
        self.assertFalse(config["omnia_toolbar"])
        self.assertFalse(config["omnia_context_menu"])
        self.assertFalse(config["omnia_shortcuts"])
        self.assertEqual(config["omnia_translate_languages"], ["en", "es"])
        self.assertEqual(config["omnia_default_translate_language"], "es")
        self.assertEqual(config["omnia_floating_panel_mode"], "blur")
        self.assertEqual(config["omnia_floating_panel_width"], "full")

    @patch("imio.omnia.tinymce.browser.viewlets.createToken")
    def test_config_json_serializes_config(self, mock_token):
        mock_token.return_value = "csrf-token"

        payload = self._make_viewlet().config_json()

        self.assertEqual(json.loads(payload)["omnia_auth_token"], "csrf-token")
