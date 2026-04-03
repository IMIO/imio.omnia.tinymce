# Design: Bundle omnia-tinymce JS into imio.omnia.tinymce

**Date:** 2026-03-23
**Status:** Approved

## Goal

Integrate the `@imiobe/omnia-tinymce` JavaScript TinyMCE plugin (from `gitlab.imio.be:ia/omnia-tinymce`) into the `imio.omnia.tinymce` Plone package so it can be served via Plone's resource registry.

## JS Source Integration (dual mode)

Two modes for getting the JS source into the Plone package:

- **Dev mode (submodule):** `ia/omnia-tinymce` is added as a git submodule at `browser/resources/`. A Makefile target runs `npm ci && npm run build` and copies `dist/` output to `browser/static/`.
- **Release mode (npm):** A `package.json` at `browser/resources/` declares `@imiobe/omnia-tinymce` as a dependency. A build script copies the installed dist files to `browser/static/`.

Both paths produce the same result: `browser/static/omnia-tinymce.js` + `browser/static/omnia-tinymce.css`, committed to git.

## Plugin Loading: TinyMCE external_plugins

The plugin is registered via the Plone registry so TinyMCE loads it on demand:

```xml
<record name="plone.tinymce.external_plugins.omnia">
  <field type="plone.registry.field.TextLine">
    <title>Omnia TinyMCE plugin</title>
  </field>
  <value>++plone++imio.omnia.tinymce/omnia-tinymce.js</value>
</record>
```

TinyMCE automatically loads external plugins when an editor initializes — no extra JS loading logic needed.

## CSS Loading: Plone resource bundle (CSS only)

The Tailwind stylesheet is registered as a lightweight CSS-only Plone bundle, loaded globally:

```xml
<records prefix="plone.resources/omnia-tinymce"
         interface="Products.CMFPlone.interfaces.IResourceRegistry">
  <value key="css">
    <element>++plone++imio.omnia.tinymce/omnia-tinymce.css</element>
  </value>
</records>

<records prefix="plone.bundles/omnia-tinymce"
         interface="Products.CMFPlone.interfaces.IBundleRegistry">
  <value key="resources">
    <element>omnia-tinymce</element>
  </value>
  <value key="enabled">True</value>
  <value key="compile">False</value>
</records>
```

The CSS is scoped to `[data-omnia]` elements with the `om:` Tailwind prefix, so global loading has no side effects. Max size: ~50 KB (enforced by CI).

## Config Bridge: JS viewlet

A viewlet injects a `<script>` that hooks into TinyMCE's init lifecycle and adds `omnia_*` options read from the Plone registry.

The viewlet:
1. Reads `IOmniaTinyMCESettings` and `IOmniaCoreSettings` from the registry
2. Serializes the relevant settings as a JSON object
3. Renders a `<script>` that listens for TinyMCE editor init and merges the config

This bridges Python-side registry settings to the JS plugin's `editor.options.get('omnia_*')` API without requiring a separate network request.

## File Layout

```
browser/
  resources/              # Git submodule (dev) or npm workspace (release)
  static/                 # Built artifacts (committed)
    omnia-tinymce.js      # ESM plugin
    omnia-tinymce.css     # Tailwind styles
  viewlets.py             # Config-bridge viewlet
  viewlets_templates/
    omnia_config.pt       # <script> template
  configure.zcml          # Updated with viewlet registration

profiles/default/registry/
  main.xml                # Updated with external_plugins + CSS bundle records
```

## Decisions

| Decision | Choice | Rationale |
|---|---|---|
| JS source mode | Submodule (dev) + npm (release) | Flexibility for active development vs. stable releases |
| Plugin loading | TinyMCE external_plugins | Idiomatic, on-demand loading by TinyMCE itself |
| CSS loading | Plone CSS-only bundle | Global but scoped, avoids complex conditional loading |
| Config bridge | JS viewlet | Clean, well-scoped to browser layer, no network requests |
| Built artifacts | Committed to git | No Node.js needed at deploy time |
