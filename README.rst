===================
imio.omnia.tinymce
===================

AI-powered text actions inside the Plone 6 TinyMCE editor, part of the
`Omnia <https://gitlab.imio.be/imio/imio.omnia>`_ suite by iMio.

This package adds a TinyMCE plugin that lets editors expand, improve, reduce,
correct, translate or make text accessible — all without leaving the rich-text
editor. It relies on ``imio.omnia.core`` for API connectivity and the shared
Omnia control panel.


Features
========

The plugin ships seven AI actions, each available from the toolbar button, the
right-click context menu, and a keyboard shortcut chord
(``Alt+O`` then an action key):

====================  ====  ===========================================================
Action                Key   Description
====================  ====  ===========================================================
Expand text           d     Make the selected text longer
Improve text          a     Enhance style and quality
Reduce text           r     Shorten the selected text
Correct text          c     Fix spelling and grammar
Make accessible       x     Simplify for WCAG / easy-read compliance
Translate text        t     Translate to a target language
Generate (*)          g     Create new content from a free-text prompt (side panel)
====================  ====  ===========================================================

(*) The *generate* action is disabled by default — it is not yet exposed by
the upstream API.

Text transformation actions open a **floating panel** near the selection (or
centred with a blur overlay, depending on the chosen mode). The *generate*
action opens a **side panel** with prompt input and a history carousel.


Installation
============

Add the egg to your buildout::

    [buildout]

    ...

    eggs =
        imio.omnia.tinymce

Then run ``bin/buildout``.

The package is auto-included in Plone via ``z3c.autoinclude.plugin``, so no
ZCML slug is needed.

``imio.omnia.core`` must be installed first. Declare the GenericSetup
dependency in your profile's ``metadata.xml`` if you build on top of this
package::

    <?xml version="1.0"?>
    <metadata>
      <version>1000</version>
      <dependencies>
        <dependency>profile-imio.omnia.tinymce:default</dependency>
      </dependencies>
    </metadata>


Configuration
=============

All settings are editable from the **TinyMCE** tab of the Omnia control panel
(Site Setup > Omnia > ``@@omnia-tinymce-settings``).

Registry settings
-----------------

Stored under the prefix ``imio.omnia.tinymce.browser.controlpanel.IOmniaTinyMCESettings``:

==============================  =====================================================================================
Field                           Purpose
==============================  =====================================================================================
``enabled_features``            Tuple of active actions (default: all except *generate*)
``show_toolbar``                Display the Omnia toolbar button (default: ``True``)
``show_context_menu``           Display entries in the context menu (default: ``True``)
``enable_shortcuts``            Enable keyboard shortcuts (default: ``True``)
``translate_languages``         Available translation language codes (default: fr, nl, de, en; all options: fr, nl,
                                de, en, es, it)
``default_translate_language``  Default target language (default: ``fr``)
``floating_panel_mode``         ``inline`` (near selection) or ``blur`` (centred overlay)
``floating_panel_width``        Width in pixels (e.g. ``500``) or ``full``
==============================  =====================================================================================


How it works
============

Plugin loading
--------------

The TinyMCE plugin is registered via three Plone registry records set by the
default GenericSetup profile:

- ``plone.custom_plugins`` — registers the ``omnia`` plugin JS
  (``++plone++imio.omnia.tinymce/omnia-tinymce.js``).
- ``plone.custom_buttons`` — adds the ``omnia`` button to the TinyMCE toolbar.
- ``plone.bundles/omnia-tinymce`` — loads the scoped CSS bundle globally.

Config bridge (viewlet)
-----------------------

An ``OmniaConfigViewlet`` registered in ``plone.htmlhead`` renders a
``<script>`` tag that monkey-patches ``tinymce.init()`` to inject ``omnia_*``
options read from the Plone registry. This bridges:

- Settings from ``IOmniaCoreSettings`` — base URL, application ID,
  municipality ID.
- Settings from ``IOmniaTinyMCESettings`` — enabled features, UI mode,
  shortcuts, translation languages, panel dimensions.
- An ``omnia_auth_token`` — a Plone CSRF authenticator token required by the
  ``@@omnia-api`` proxy for every POST request.

API requests go through the ``@@omnia-api`` proxy view provided by
``imio.omnia.core``, so no API credentials are exposed to the browser. By
default, callers must have the
``imio.omnia.core: Access Omnia API proxy`` permission, which
``imio.omnia.core`` grants to ``Authenticated`` users.

Uninstall
---------

The uninstall handler removes the ``omnia`` entries from
``plone.custom_plugins`` and ``plone.custom_buttons``, and disables the CSS
bundle.


Frontend development
====================

The TinyMCE plugin source lives in ``browser/resources/`` as a **git
submodule** (``ia/omnia-tinymce``). Built artifacts are committed to
``browser/static/``.

Rebuild after JS changes::

    make build-js          # npm ci + vite build + copy to static/
    make clean-js          # remove built artifacts

Run the Storybook dev environment::

    make dev               # Storybook on http://localhost:6006

The frontend stack uses **Vite** (library mode), **Preact**, **Tailwind CSS
v4** (``om:`` prefix, scoped to ``[data-omnia]``), and **Motion** for drag /
resize.


Translations
============

This product has been translated into:

- English
- French


Authors
=======

- `iMio, SCRL <https://imio.be>`_
- Antoine Duchene


License
=======

The project is licensed under the GPLv2.
