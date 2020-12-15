import os
import subprocess
from django.conf import settings
from django.core import management
from django.test import TestCase, override_settings

from .utils import build_static_assets


@override_settings(
    STATIC_ROOT=os.path.join(settings.BASE_DIR, 'static_compressed'),
    STATICFILES_STORAGE=('whitenoise.storage.'
                         'CompressedManifestStaticFilesStorage')
)
class CompressedCollectStaticTests(TestCase):
    '''
    This tests to make sure we can collect static assets using
    Django's compressed static file storage, which actually introspects into
    CSS files to make sure they refer to assets that actually exist
    (e.g. background images).
    '''

    def test_it_works(self):
        build_static_assets()
        management.call_command('collectstatic', '--noinput', verbosity=0)
        subprocess.check_call(['rm', '-rf', settings.STATIC_ROOT])
