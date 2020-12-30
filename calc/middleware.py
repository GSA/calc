from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from debug_toolbar.middleware import DebugToolbarMiddleware
from django.contrib.auth.signals import user_logged_out


def iam_logged_out_actions(sender, user, request, **kwargs):
    print("logging out: " + str(user))


user_logged_out.connect(iam_logged_out_actions)


class ComplianceMiddleware:
    '''
    Middleware to add security-related response headers.

    If the SECURITY_HEADERS_ON_ERROR_ONLY setting is True, then the headers
    will only be added to error responses (400 and above). This behavior is
    needed for cloud.gov deployments because its proxy adds the headers
    to 200 responses, but not to error responses.

    Otherwise, the headers will be added to all responses.

    We also want to ensure that /admin/ routes are never cached, so we'll
    add appropriate headers for those routes.
    '''

    def process_response(self, request, response):
        if (not settings.SECURITY_HEADERS_ON_ERROR_ONLY or
                response.status_code >= 400):

            response["X-Content-Type-Options"] = "nosniff"
            response["X-XSS-Protection"] = "1; mode=block"

        if request.path.startswith("/admin/"):
            response["Cache-Control"] = "no-cache"

        return response


def show_toolbar(request):
    '''
    Like debug_toolbar.middleware.show_toolbar, but without the
    INTERNAL_IPS consultation, since the developer may be using
    Docker or accessing their development instance over a mobile/tablet
    device.
    '''

    if not settings.DEBUG:
        raise AssertionError("I should not be used when DEBUG is False!")

    if request.is_ajax():
        return False

    for prefix in settings.DEBUG_TOOLBAR_DISABLE_FOR_URL_PREFIXES:
        if request.path.startswith(prefix):
            return False

    return True


class DebugOnlyDebugToolbarMiddleware(DebugToolbarMiddleware):
    '''
    Like DebugToolbarMiddleware, but tells Django it's unused if
    DEBUG or HIDE_DEBUG_UI is False.
    '''

    def __init__(self):
        if not settings.DEBUG or settings.HIDE_DEBUG_UI:
            raise MiddlewareNotUsed()
        super().__init__()
