# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
)
from plone.testing import z2

import imio.omnia.tinymce
from imio.omnia.core.testing import IMIO_OMNIA_CORE_FIXTURE


class ImioOmniaTinyMCELayer(PloneSandboxLayer):

    defaultBases = (IMIO_OMNIA_CORE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=imio.omnia.tinymce)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'imio.omnia.tinymce:default')


IMIO_OMNIA_TINYMCE_FIXTURE = ImioOmniaTinyMCELayer()


IMIO_OMNIA_TINYMCE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(IMIO_OMNIA_TINYMCE_FIXTURE,),
    name='ImioOmniaTinyMCELayer:IntegrationTesting',
)


IMIO_OMNIA_TINYMCE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(IMIO_OMNIA_TINYMCE_FIXTURE,),
    name='ImioOmniaTinyMCELayer:FunctionalTesting',
)


IMIO_OMNIA_TINYMCE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        IMIO_OMNIA_TINYMCE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='ImioOmniaTinyMCELayer:AcceptanceTesting',
)
