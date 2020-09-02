try:
    from django.core.urlresolvers import reverse  # NOQA  pragma: no cover
except ImportError:  # pragma: no cover
    # Django 2.0+
    from django.urls import reverse  # NOQA  pragma: no cover
import django.contrib.auth
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.utils.crypto import get_random_string
from django.conf import settings
from urllib.parse import urlencode
from contracts.models import ScheduleMetadata
from django.http import HttpResponseRedirect


def about(request):
    return render(request, 'about.html', {
        'current_selected_tab': 'about',
        'schedules': ScheduleMetadata.objects.all().order_by('sin'),
    })


def estimating_tool(request):
    return render(request, 'estimating_tool.html', {'current_selected_tab': 'estimating_tool'})


def step_cap(request):
    from django import forms
    CHOICES = [('1', 'First'), ('2', 'Second')]
    return render(request, 'step_cap.html', {
        'current_selected_tab': 'capability_statement',
        'django_form': forms,
        'django_radio_choices': CHOICES,
    })


def index(request, template_vars=None):
    return render(request, 'index.html', template_vars or {})


def uaa_logout(request):
    redirect_uri = request.build_absolute_uri(reverse('logout'))
    url = settings.UAA_LOGOUT_URL + '?' + urlencode({
        'client_id': settings.UAA_CLIENT_ID,
        'redirect': redirect_uri,
    })
    print(url)
    return HttpResponseRedirect(url)


def logout(request):
    django.contrib.auth.logout(request)
    return render(request, 'logged_out.html')


# TODO: Re-enable this eventually. Right now we can't use it because
# we need to use New Relic for front-end error monitoring, and it doesn't
# support CSP in any way.
def index_with_csp(request):
    csp_nonce = get_random_string(length=10)
    response = index(request, template_vars={
        'csp_nonce': mark_safe('nonce="{}"'.format(csp_nonce))  # nosec
    })
    script_src = ' '.join([
        "'self'",
        "*.googleapis.com",
        "dap.digitalgov.gov",
        "www.google-analytics.com",
        "ethn.io",
        # Browsers that don't support CSP v2 need this to work.
        "'unsafe-inline'",
        # For browsers that *do* support CSP v2, the following will
        # override our earlier 'unsafe-inline' directive.
        "'nonce-{}'".format(csp_nonce)
    ])
    response['Content-Security-Policy'] = '; '.join([
        "default-src *",
        "script-src {}".format(script_src),
        "style-src * 'unsafe-inline'",
        "img-src * data:",
    ])
    return response
