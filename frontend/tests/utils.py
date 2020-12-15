import os
import subprocess


_static_assets_built = 'SKIP_STATIC_ASSET_BUILDING' in os.environ


def build_static_assets():
    '''
    Builds static assets needed by the Django project (e.g.,
    JS and CSS bundles).
    '''

    global _static_assets_built

    if not _static_assets_built:
        subprocess.check_call(['yarn', 'gulp', 'build'])
        _static_assets_built = True
