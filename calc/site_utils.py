from django.contrib.sites.models import Site
from django.conf import settings
from django.core.urlresolvers import reverse


def absolutify_url(url: str) -> str:
    '''
    If the URL is an absolute path, returns the URL prefixed with
    the current Site's protocol and host information.

    If the given URL is already absolute, returns the URL unchanged.
    '''

    if url.startswith('http://') or url.startswith('https://'):
        return url

    if not url.startswith('/'):
        raise ValueError(f"url must be an absolute path: {url}")

    protocol = 'https'
    host = Site.objects.get_current().domain
    if ((settings.DEBUG and not settings.DEBUG_HTTPS) or
            not settings.SECURE_SSL_REDIRECT):
        protocol = 'http'
    return f"{protocol}://{host}{url}"


def absolute_reverse(*args, **kwargs) -> str:
    '''
    Like Django's reverse(), but ensures the URL includes protocol
    and host information for the current Site, so that it can be
    embedded in an external location, e.g. an email.
    '''

    return absolutify_url(reverse(*args, **kwargs))


def get_canonical_url(request):
    '''
    Get the canonical URL for the given request, using the current
    Site's configuration.
    '''

    return absolutify_url(request.get_full_path())
