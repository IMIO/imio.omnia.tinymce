# Bundle omnia-tinymce JS into imio.omnia.tinymce — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Integrate the `@imiobe/omnia-tinymce` JavaScript TinyMCE plugin into the Plone package so it is served via the resource registry, with settings bridged from Plone to the JS plugin.

**Architecture:** The JS project (`gitlab.imio.be:ia/omnia-tinymce`) is added as a git submodule at `browser/resources/`. Built artifacts (`omnia-tinymce.js` + `.css`) are committed into `browser/static/`, already registered via `<plone:static>`. The plugin is loaded by TinyMCE via `plone.custom_plugins` registry record. CSS is loaded globally via a Plone CSS-only bundle. A viewlet bridges Plone registry settings to TinyMCE init options.

**Tech Stack:** Plone 6, TinyMCE 6+, Vite (build), Preact, Tailwind CSS v4, plone.app.registry, z3c.jbot

**Design doc:** `docs/plans/2026-03-23-tinymce-js-bundling-design.md`

---

### Task 1: Add git submodule for omnia-tinymce JS source

**Files:**
- Create: `.gitmodules` entry
- Create: `src/imio/omnia/tinymce/browser/resources/` (submodule mount)

**Step 1: Add the submodule**

```bash
cd src/imio.omnia.tinymce
git submodule add git@gitlab.imio.be:ia/omnia-tinymce.git src/imio/omnia/tinymce/browser/resources
```

**Step 2: Verify submodule is checked out**

```bash
ls src/imio/omnia/tinymce/browser/resources/package.json
```

Expected: file exists

**Step 3: Commit**

```bash
git add .gitmodules src/imio/omnia/tinymce/browser/resources
git commit -m "feat: add omnia-tinymce JS project as submodule at browser/resources"
```

---

### Task 2: Build JS artifacts and commit to browser/static/

**Files:**
- Modify: `src/imio/omnia/tinymce/browser/static/` (add built files)
- Create: `Makefile`

**Step 1: Install dependencies and build**

```bash
cd src/imio.omnia.tinymce/src/imio/omnia/tinymce/browser/resources
npm ci
npm run build
```

Expected: `dist/omnia-tinymce.js`, `dist/omnia-tinymce.css`, `dist/omnia-tinymce.umd.cjs` created.

**Step 2: Copy built artifacts to browser/static/**

```bash
cp dist/omnia-tinymce.js ../static/omnia-tinymce.js
cp dist/omnia-tinymce.css ../static/omnia-tinymce.css
```

**Step 3: Remove the .gitkeep placeholder**

```bash
rm -f src/imio/omnia/tinymce/browser/static/.gitkeep
```

**Step 4: Create Makefile at package root**

Create `src/imio.omnia.tinymce/Makefile`:

```makefile
JS_SRC = src/imio/omnia/tinymce/browser/resources
STATIC  = src/imio/omnia/tinymce/browser/static

.PHONY: build-js clean-js

build-js:
	cd $(JS_SRC) && npm ci && npm run build
	cp $(JS_SRC)/dist/omnia-tinymce.js  $(STATIC)/omnia-tinymce.js
	cp $(JS_SRC)/dist/omnia-tinymce.css $(STATIC)/omnia-tinymce.css

clean-js:
	rm -f $(STATIC)/omnia-tinymce.js $(STATIC)/omnia-tinymce.css
```

**Step 5: Verify built files are serveable**

```bash
ls -la src/imio/omnia/tinymce/browser/static/omnia-tinymce.*
```

Expected: both `.js` and `.css` files present.

**Step 6: Commit**

```bash
cd src/imio.omnia.tinymce
git add Makefile src/imio/omnia/tinymce/browser/static/omnia-tinymce.js src/imio/omnia/tinymce/browser/static/omnia-tinymce.css
git rm --cached src/imio/omnia/tinymce/browser/static/.gitkeep 2>/dev/null || true
git commit -m "feat: add built omnia-tinymce JS/CSS artifacts and Makefile"
```

---

### Task 3: Register plugin via custom_plugins and CSS bundle in registry

**Files:**
- Modify: `src/imio/omnia/tinymce/profiles/default/registry/main.xml`

Plone 6 reads `plone.custom_plugins` (a `List[TextLine]` on `ITinyMCESchema`) and populates `external_plugins` in the TinyMCE init config. Format: `pluginname|url`.

**Step 1: Write the test**

Add to `src/imio/omnia/tinymce/tests/test_setup.py`, in class `TestSetup`:

```python
def test_tinymce_custom_plugin_registered(self):
    """Test that the omnia plugin is registered in TinyMCE custom_plugins."""
    from plone.registry.interfaces import IRegistry
    from zope.component import getUtility

    registry = getUtility(IRegistry)
    custom_plugins = registry.get("plone.custom_plugins", [])
    matching = [p for p in custom_plugins if p.startswith("omnia|")]
    self.assertEqual(len(matching), 1)
    self.assertIn("++plone++imio.omnia.tinymce/omnia-tinymce.js", matching[0])

def test_css_bundle_registered(self):
    """Test that the omnia-tinymce CSS bundle is registered."""
    from plone.registry.interfaces import IRegistry
    from zope.component import getUtility

    registry = getUtility(IRegistry)
    bundle_enabled = registry.get("plone.bundles/omnia-tinymce.enabled", None)
    self.assertTrue(bundle_enabled)
```

**Step 2: Run tests to verify they fail**

```bash
cd ../../.. && bin/test -s imio.omnia.tinymce -t test_tinymce_custom_plugin -t test_css_bundle -v
```

Expected: FAIL (records don't exist yet)

**Step 3: Update registry/main.xml**

Replace the contents of `src/imio/omnia/tinymce/profiles/default/registry/main.xml`:

```xml
<?xml version="1.0"?>
<registry
    xmlns:i18n="http://xml.zope.org/namespaces/i18n"
    i18n:domain="imio.omnia.tinymce">

  <records interface="imio.omnia.tinymce.browser.controlpanel.IOmniaTinyMCESettings"/>

  <!-- Register omnia as a TinyMCE external plugin via plone.custom_plugins -->
  <record name="plone.custom_plugins">
    <value purge="false">
      <element>omnia|++plone++imio.omnia.tinymce/omnia-tinymce.js</element>
    </value>
  </record>

  <!-- Add "omnia" to the TinyMCE toolbar -->
  <record name="plone.custom_buttons">
    <value purge="false">
      <element>omnia</element>
    </value>
  </record>

  <!-- CSS-only resource -->
  <records prefix="plone.resources/omnia-tinymce"
           interface="Products.CMFPlone.interfaces.IResourceRegistry">
    <value key="css">
      <element>++plone++imio.omnia.tinymce/omnia-tinymce.css</element>
    </value>
  </records>

  <!-- CSS-only bundle -->
  <records prefix="plone.bundles/omnia-tinymce"
           interface="Products.CMFPlone.interfaces.IBundleRegistry">
    <value key="resources">
      <element>omnia-tinymce</element>
    </value>
    <value key="enabled">True</value>
    <value key="compile">False</value>
  </records>

</registry>
```

**Step 4: Run tests to verify they pass**

```bash
bin/test -s imio.omnia.tinymce -t test_tinymce_custom_plugin -t test_css_bundle -v
```

Expected: PASS

**Step 5: Commit**

```bash
cd src/imio.omnia.tinymce
git add src/imio/omnia/tinymce/profiles/default/registry/main.xml src/imio/omnia/tinymce/tests/test_setup.py
git commit -m "feat: register omnia TinyMCE plugin and CSS bundle in resource registry"
```

---

### Task 4: Create the config-bridge viewlet

**Files:**
- Create: `src/imio/omnia/tinymce/browser/viewlets.py`
- Create: `src/imio/omnia/tinymce/browser/viewlets_templates/omnia_config.pt`
- Modify: `src/imio/omnia/tinymce/browser/configure.zcml`

The viewlet reads `IOmniaTinyMCESettings` + `IOmniaCoreSettings` from the Plone registry, serializes the settings as JSON, and renders a `<script>` that patches TinyMCE's init config before the editor loads.

**Step 1: Write the test**

Add to `src/imio/omnia/tinymce/tests/test_setup.py`, in class `TestSetup`:

```python
def test_omnia_config_viewlet_registered(self):
    """Test that the omnia-config viewlet is registered."""
    from zope.viewlet.interfaces import IViewletManager
    from zope.component import queryMultiAdapter
    from zope.interface import alsoProvides
    from imio.omnia.tinymce.interfaces import IImioOmniaTinyMCELayer

    request = self.layer["request"]
    alsoProvides(request, IImioOmniaTinyMCELayer)

    portal = self.portal
    view = queryMultiAdapter((portal, request), name="plone_layout")
    manager = queryMultiAdapter(
        (portal, request, view),
        IViewletManager,
        "plone.htmlhead",
    )
    self.assertIsNotNone(manager)
    manager.update()
    viewlet_names = [v.__name__ for v in manager.viewlets]
    self.assertIn("omnia-tinymce-config", viewlet_names)
```

**Step 2: Run test to verify it fails**

```bash
cd ../../.. && bin/test -s imio.omnia.tinymce -t test_omnia_config_viewlet -v
```

Expected: FAIL

**Step 3: Create the viewlet Python module**

Create `src/imio/omnia/tinymce/browser/viewlets.py`:

```python
# -*- coding: utf-8 -*-
import json

from plone import api
from plone.app.layout.viewlets.common import ViewletBase


class OmniaConfigViewlet(ViewletBase):
    """Inject omnia_* TinyMCE options from the Plone registry into the page."""

    def available(self):
        return True

    def get_omnia_config(self):
        core_prefix = "imio.omnia.core.browser.controlpanel.IOmniaCoreSettings"
        tmce_prefix = "imio.omnia.tinymce.browser.controlpanel.IOmniaTinyMCESettings"

        def _get(key, default=None):
            try:
                return api.portal.get_registry_record(key)
            except (KeyError, api.exc.InvalidParameterError):
                return default

        config = {}

        # From IOmniaCoreSettings
        base_url = _get(f"{core_prefix}.core_api_url", "")
        if base_url:
            config["omnia_base_url"] = base_url
        application = _get(f"{core_prefix}.application_id", "")
        if application:
            config["omnia_application"] = application
        organization = _get(f"{core_prefix}.organization_id", "")
        if organization:
            config["omnia_municipality"] = organization

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

    def omnia_config_json(self):
        return json.dumps(self.get_omnia_config())
```

**Step 4: Create the viewlet template**

Create directory and template `src/imio/omnia/tinymce/browser/viewlets_templates/omnia_config.pt`:

```html
<script tal:define="config view/omnia_config_json"
        tal:condition="config"
        tal:attributes="data-omnia-config config"
        type="text/javascript">
(function() {
  var configEl = document.currentScript;
  var omniaConfig = JSON.parse(configEl.getAttribute('data-omnia-config'));

  document.addEventListener('DOMContentLoaded', function() {
    if (typeof tinymce === 'undefined') return;

    var origInit = tinymce.init;
    tinymce.init = function(settings) {
      for (var key in omniaConfig) {
        if (omniaConfig.hasOwnProperty(key)) {
          settings[key] = omniaConfig[key];
        }
      }
      return origInit.call(tinymce, settings);
    };
  });
})();
</script>
```

**Step 5: Register the viewlet in configure.zcml**

Add to `src/imio/omnia/tinymce/browser/configure.zcml`, before the closing `</configure>`:

```xml
  <browser:viewlet
    name="omnia-tinymce-config"
    for="*"
    manager="plone.app.layout.viewlets.interfaces.IHtmlHead"
    class=".viewlets.OmniaConfigViewlet"
    template="viewlets_templates/omnia_config.pt"
    permission="zope2.View"
    layer="imio.omnia.tinymce.interfaces.IImioOmniaTinyMCELayer"
  />
```

**Step 6: Run tests to verify they pass**

```bash
cd ../../.. && bin/test -s imio.omnia.tinymce -v
```

Expected: all tests PASS

**Step 7: Commit**

```bash
cd src/imio.omnia.tinymce
git add src/imio/omnia/tinymce/browser/viewlets.py \
        src/imio/omnia/tinymce/browser/viewlets_templates/omnia_config.pt \
        src/imio/omnia/tinymce/browser/configure.zcml \
        src/imio/omnia/tinymce/tests/test_setup.py
git commit -m "feat: add config-bridge viewlet to inject omnia settings into TinyMCE"
```

---

### Task 5: Write viewlet config serialization test

**Files:**
- Modify: `src/imio/omnia/tinymce/tests/test_setup.py`

**Step 1: Write the test**

Add to `src/imio/omnia/tinymce/tests/test_setup.py`, in class `TestSetup`:

```python
def test_omnia_config_viewlet_contains_settings(self):
    """Test that the viewlet serializes registry settings correctly."""
    from zope.component import queryMultiAdapter
    from zope.interface import alsoProvides
    from imio.omnia.tinymce.interfaces import IImioOmniaTinyMCELayer
    import json

    request = self.layer["request"]
    alsoProvides(request, IImioOmniaTinyMCELayer)

    # Set a registry value to check it appears in the config
    api.portal.set_registry_record(
        "imio.omnia.tinymce.browser.controlpanel.IOmniaTinyMCESettings.enabled_features",
        ("improve-text", "correct-text"),
    )

    viewlet = queryMultiAdapter(
        (self.portal, request, None, None),
        name="omnia-tinymce-config",
    )
    self.assertIsNotNone(viewlet)
    config = json.loads(viewlet.omnia_config_json())
    self.assertEqual(config["omnia_enabled_features"], ["improve-text", "correct-text"])
    self.assertIn("omnia_toolbar", config)
```

**Step 2: Run tests**

```bash
cd ../../.. && bin/test -s imio.omnia.tinymce -t test_omnia_config_viewlet_contains -v
```

Expected: PASS

**Step 3: Commit**

```bash
cd src/imio.omnia.tinymce
git add src/imio/omnia/tinymce/tests/test_setup.py
git commit -m "test: add config serialization test for omnia viewlet"
```

---

### Task 6: Add uninstall cleanup for registry records

**Files:**
- Create or modify: `src/imio/omnia/tinymce/profiles/uninstall/registry.xml`

On uninstall, the `custom_plugins` and `custom_buttons` entries should be removed, and the CSS bundle disabled.

**Step 1: Write the test**

Add to `src/imio/omnia/tinymce/tests/test_setup.py`, in class `TestUninstall`:

```python
def test_tinymce_custom_plugin_removed(self):
    """Test that the omnia plugin is removed from custom_plugins on uninstall."""
    from plone.registry.interfaces import IRegistry
    from zope.component import getUtility

    registry = getUtility(IRegistry)
    custom_plugins = registry.get("plone.custom_plugins", [])
    matching = [p for p in custom_plugins if p.startswith("omnia|")]
    self.assertEqual(len(matching), 0)

def test_css_bundle_disabled(self):
    """Test that the CSS bundle is disabled on uninstall."""
    from plone.registry.interfaces import IRegistry
    from zope.component import getUtility

    registry = getUtility(IRegistry)
    enabled = registry.get("plone.bundles/omnia-tinymce.enabled", None)
    self.assertFalse(enabled)
```

**Step 2: Run tests to verify they fail**

```bash
cd ../../.. && bin/test -s imio.omnia.tinymce -t test_tinymce_custom_plugin_removed -t test_css_bundle_disabled -v
```

Expected: FAIL

**Step 3: Update setuphandlers.py with uninstall logic**

Modify `src/imio/omnia/tinymce/setuphandlers.py`, update the `uninstall` function:

```python
def uninstall(context):
    """Uninstall script"""
    from plone.registry.interfaces import IRegistry
    from zope.component import getUtility

    registry = getUtility(IRegistry)

    # Remove omnia from custom_plugins
    key = "plone.custom_plugins"
    current = list(registry.get(key, []))
    registry[key] = tuple(p for p in current if not p.startswith("omnia|"))

    # Remove omnia from custom_buttons
    key = "plone.custom_buttons"
    current = list(registry.get(key, []))
    registry[key] = tuple(p for p in current if p != "omnia")

    # Disable CSS bundle
    bundle_key = "plone.bundles/omnia-tinymce.enabled"
    if bundle_key in registry.records:
        registry[bundle_key] = False
```

**Step 4: Run tests to verify they pass**

```bash
cd ../../.. && bin/test -s imio.omnia.tinymce -v
```

Expected: all tests PASS

**Step 5: Commit**

```bash
cd src/imio.omnia.tinymce
git add src/imio/omnia/tinymce/setuphandlers.py src/imio/omnia/tinymce/tests/test_setup.py
git commit -m "feat: clean up registry records on uninstall"
```

---

### Task 7: Update CLAUDE.md and package metadata

**Files:**
- Modify: `CLAUDE.md`
- Modify: `setup.py` (if dependency on `collective.z3cform.datagridfield` is missing)
- Modify: `src/imio/omnia/tinymce/profiles/default/metadata.xml` (add `imio.omnia.core` dependency)

**Step 1: Update metadata.xml to declare dependency on imio.omnia.core**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<metadata>
  <version>1001</version>
  <dependencies>
    <dependency>profile-imio.omnia.core:default</dependency>
  </dependencies>
</metadata>
```

**Step 2: Update CLAUDE.md**

Add the JS bundling and resource registry sections to `CLAUDE.md` to reflect the new architecture (submodule, Makefile, viewlet, registry records).

**Step 3: Run full test suite**

```bash
cd ../../.. && bin/test -s imio.omnia.tinymce -v
```

Expected: all tests PASS

**Step 4: Commit**

```bash
cd src/imio.omnia.tinymce
git add CLAUDE.md src/imio/omnia/tinymce/profiles/default/metadata.xml
git commit -m "docs: update CLAUDE.md and metadata for JS bundling integration"
```

---

### Task 8: Manual integration smoke test

**Files:** None (verification only)

**Step 1: Start the Plone instance**

```bash
cd ../../.. && bin/instance fg
```

**Step 2: Verify static resources are accessible**

Open in browser:
- `http://localhost:8080/Plone/++plone++imio.omnia.tinymce/omnia-tinymce.js`
- `http://localhost:8080/Plone/++plone++imio.omnia.tinymce/omnia-tinymce.css`

Expected: both files load with correct content.

**Step 3: Verify the TinyMCE plugin loads**

1. Go to any content edit form with a rich text field
2. Open browser dev console
3. Check that `tinymce.PluginManager.get('omnia')` returns a truthy value
4. Check the TinyMCE toolbar shows the Omnia button

**Step 4: Verify the config viewlet**

1. View page source on an edit form
2. Search for `data-omnia-config`
3. Verify the JSON contains expected keys (`omnia_enabled_features`, `omnia_toolbar`, etc.)

**Step 5: Verify CSS is loaded**

1. Inspect the `<head>` of any page
2. Confirm a `<link>` or `<style>` tag references `omnia-tinymce.css`
