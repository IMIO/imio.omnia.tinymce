Changelog
=========


1.0a4 (2026-04-03)
------------------

- Update the JS bundle.
  [aduchene]


1.0a3 (2026-04-03)
------------------

- Load imio.omnia.core ZCML.
  [aduchene]


1.0a2 (2026-04-03)
------------------

- Re-release because ZCML files were lacking.
  [aduchene]


1.0a1 (2026-04-03)
------------------

- Initial release.
  [duchenean]
- Added TinyMCE AI plugin with 7 text actions: generate, expand, improve,
  reduce, correct, translate, and make accessible.
  [duchenean]
- Added toolbar button, context menu entry, and keyboard shortcuts for
  triggering AI actions on selected text.
  [duchenean]
- Added floating panel with two display modes: ``inline`` (near selection)
  and ``blur`` (centred with overlay), with configurable width.
  [duchenean]
- Added translation support with 6 languages (fr, nl, de, en, es, it) and
  configurable default target language.
  [duchenean]
- Added control panel tab (``@@omnia-tinymce-settings``) in the shared
  Omnia settings UI: per-feature enable/disable, toolbar/context menu/shortcut
  toggles, translation languages, and panel display settings.
  [duchenean]
- Added viewlet config bridge injecting Omnia settings into TinyMCE init
  via monkey-patched ``tinymce.init``.
  [duchenean]
- Added TinyMCE plugin registration via ``plone.custom_plugins`` and CSS
  bundle via ``plone.bundles/omnia-tinymce`` with Tailwind CSS scoped to
  ``[data-omnia]``.
  [duchenean]
- Added clean uninstall removing plugin registrations and CSS bundle.
  [duchenean]
- Added i18n support (en, fr).
  [duchenean]
