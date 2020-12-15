# This middleware + static file storage backend makes development behave more
# like production by disallowing references to nonexistent files from being
# generated in templates.

from django.contrib.staticfiles.storage import StaticFilesStorage
from django.contrib.staticfiles import finders
from whitenoise.middleware import WhiteNoiseMiddleware


class CrotchetyWhiteNoiseMiddleware(WhiteNoiseMiddleware):
    def get_name_without_hash(self, filename):
        # The default implementation of this sometimes returns
        # the names of nonexistent files (e.g. converting files with
        # .min.js extensions to just .js) which then makes the static
        # file storage backend throw an exception.
        #
        # Since this middleware should only be used in development,
        # where hashes are never included as part of filenames, we'll
        # just return the filename here.
        return filename


class CrotchetyFileNotFoundError(Exception):
    pass


class CrotchetyStaticFilesStorage(StaticFilesStorage):
    def url(self, name):
        foundpath = finders.find(name)

        if not foundpath:
            raise CrotchetyFileNotFoundError('Cannot find %s' % name)

        return super().url(name)
