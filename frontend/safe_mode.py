from django.http import HttpResponseRedirect
from django.conf.urls import url
from django.views.decorators.http import require_POST


SESSION_KEY = 'enable_safe_mode'


def is_enabled(request):
    return request.session.get(SESSION_KEY, False)


@require_POST
def enable(request):
    request.session[SESSION_KEY] = True
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@require_POST
def disable(request):
    request.session[SESSION_KEY] = False
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


urlpatterns = [
    url('^enable$', enable, name='enable'),
    url('^disable$', disable, name='disable'),
]
