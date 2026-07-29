# imio.omnia.tinymce

Plone 6 add-on that integrates iMio's Omnia AI features into the TinyMCE rich-text editor. Provides AI-powered text actions (expand, improve, reduce, correct, translate, make accessible) configurable through a control panel that lives as a tab in the shared Omnia settings UI from `imio.omnia.core`.

## Project layout

```
src/imio/omnia/tinymce/
├── browser/
│   ├── action.py               # Browser view base
│   ├── controlpanel.py         # @@omnia-tinymce-settings registry form
│   ├── viewlets.py             # OmniaConfigViewlet — bridges registry settings to TinyMCE
│   ├── viewlets_templates/
│   │   └── omnia_config.pt     # <script> injecting omnia_* options into TinyMCE init
│   ├── configure.zcml          # Browser views, static resources, viewlet, jbot overrides
│   ├── overrides/              # z3c.jbot template overrides
│   ├── resources/              # Git submodule → ia/omnia-tinymce (JS source, dev/testing only, not used to build static/)
│   ├── npm/                    # Pins the published @imiobe/omnia-tinymce npm version (package.json + lockfile)
│   └── static/                 # Built JS/CSS artifacts served via ++plone++imio.omnia.tinymce
│       ├── omnia-tinymce.js    # ESM TinyMCE plugin (copied from the pinned npm package's dist/)
│       └── omnia-tinymce.css   # Tailwind CSS styles (scoped to [data-omnia])
├── profiles/
│   ├── default/                # GenericSetup install profile
│   │   ├── actions.xml         # Portal actions (control panel tab)
│   │   ├── browserlayer.xml    # Browser layer registration
│   │   ├── catalog.xml         # Catalog configuration
│   │   ├── metadata.xml        # Profile metadata & dependencies (requires imio.omnia.core)
│   │   ├── registry/           # Plone registry records
│   │   │   └── main.xml        # Settings + custom_plugins + CSS bundle
│   │   └── rolemap.xml         # Role-permission mappings
│   └── uninstall/              # GenericSetup uninstall profile
├── locales/                    # i18n (en)
├── tests/                      # test_setup.py, robot tests
├── __init__.py                 # Message factory (_)
├── interfaces.py               # IImioOmniaTinyMCELayer
├── testing.py                  # IMIO_OMNIA_TINYMCE_*_TESTING fixtures
├── setuphandlers.py            # HiddenProfiles, post_install, uninstall hooks
├── configure.zcml              # Root ZCML — profiles, permissions, browser include
└── permissions.zcml            # Permission definitions
```

## Frontend (JS/CSS)

The TinyMCE plugin is published as the npm package `@imiobe/omnia-tinymce`. `browser/npm/package.json` pins the version consumed by this add-on; built artifacts (`dist/omnia-tinymce.umd.cjs` and `dist/omnia-tinymce.css`) are copied from that package into `browser/static/`, which is committed to the repo.

The source also lives at `browser/resources/` as a **git submodule** pointing to `gitlab.imio.be:ia/omnia-tinymce`, but it is only for local development/testing of JS changes before they're published to npm — it is **not** used to produce the shipped artifacts.

### Updating the JS bundle

```bash
make update-js                  # npm install (in browser/npm/) + copy dist/ to static/
make clean-js                   # Remove built artifacts from static/
```

To bump to a newer published version: edit the version in `src/imio/omnia/tinymce/browser/npm/package.json`, run `make update-js`, then commit `package.json`, `package-lock.json`, and the regenerated `static/omnia-tinymce.js` / `static/omnia-tinymce.css`.

### How the plugin is loaded

1. **Plugin JS** — Registered via `plone.custom_plugins` registry record (`omnia|++plone++imio.omnia.tinymce/omnia-tinymce.js`). TinyMCE loads it automatically via `external_plugins`.
2. **Plugin CSS** — Registered as a Plone CSS-only bundle (`plone.bundles/omnia-tinymce`), loaded globally. CSS is scoped to `[data-omnia]` with `om:` Tailwind prefix — no side effects.
3. **Toolbar button** — Added via `plone.custom_buttons` registry record.

### Config bridge (viewlet)

The `OmniaConfigViewlet` (registered in `plone.htmlhead`) renders a `<script>` that monkey-patches `tinymce.init` to inject `omnia_*` options read from the Plone registry. This bridges:

- `IOmniaCoreSettings` → `omnia_base_url`, `omnia_application`, `omnia_municipality`
- `IOmniaTinyMCESettings` → `omnia_enabled_features`, `omnia_toolbar`, `omnia_context_menu`, `omnia_shortcuts`, `omnia_translate_languages`, `omnia_default_translate_language`, `omnia_floating_panel_mode`, `omnia_floating_panel_width`

### Uninstall

`setuphandlers.uninstall()` removes the `omnia` entries from `plone.custom_plugins` and `plone.custom_buttons`, and disables the CSS bundle.

## Development

This package is developed inside the parent `imio.omnia` buildout. From the buildout root (`../../..`):

```bash
bin/buildout                    # Install all develop eggs
bin/instance fg                 # Start Plone on port 8080 (admin:admin)
```

### Running tests

From this package directory:

```bash
tox -e py312-Plone61            # Run tests against Plone 6.1
tox -l                          # List all test environments
```

Or via the parent buildout:

```bash
../../bin/test -s imio.omnia.tinymce
```

### Code quality

```bash
tox -e black-check              # Check formatting
tox -e black-enforce            # Apply formatting
tox -e py312-lint               # isort + flake8
tox -e isort-apply              # Fix import order
```

## Code style

- Formatter: **Black** (line length 120)
- Import sorting: **isort** with `profile = plone`
- Linter: **flake8** (ignores: W503, C812, E501, T001, C813, C101)
- i18n domain: `imio.omnia.tinymce` — use `from imio.omnia.tinymce import _` for message strings
- Editor config: 4-space indent for Python/cfg, 2-space for XML/HTML/JS

## Registry settings

Stored under `imio.omnia.tinymce.browser.controlpanel.IOmniaTinyMCESettings`:

- `enabled_features` — Tuple of active AI features: `generate`, `expand-text`, `improve-text`, `reduce-text`, `correct-text`, `make-accessible`, `translate-text`
- `show_toolbar` — Show TinyMCE toolbar button (default: True)
- `show_context_menu` — Show context menu entry (default: True)
- `enable_shortcuts` — Enable keyboard shortcuts (default: True)
- `translate_languages` — Available language codes for translation (fr, nl, de, en, es, it)
- `default_translate_language` — Default target language (default: fr)
- `floating_panel_mode` — Display mode: `inline` (near selection) or `blur` (centred with overlay)
- `floating_panel_width` — Panel width in pixels or `full` for full viewport

## Architecture notes

- Depends on `imio.omnia.core` for the shared control panel wrapper (`OmniaCoreControlPanelFormWrapper`) and core API infrastructure.
- Auto-included in Plone via `z3c.autoinclude.plugin` entry point (target: `plone`).
- Browser layer `IImioOmniaTinyMCELayer` gates all views and overrides — only active when the add-on is installed.
- Namespace packages: `imio`, `imio.omnia` — shared across sibling packages.
- Control panel view registered at `@@omnia-tinymce-settings`, requires `cmf.ManagePortal`.
- Uses `collective.z3cform.datagridfield` for the `omnia_endpoints` widget.
