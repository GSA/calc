from django.conf import settings
# from django.conf.urls import include, url
from django.urls import include, re_path, path
from django.contrib import admin
from django.views.generic import TemplateView
from uaa_client.decorators import staff_login_required

import data_explorer.views
import contracts.views
from .sample_users import login_sample_user
from .healthcheck import healthcheck
from .robots import robots_txt
from .changelog import django_view as view_changelog

# Wrap the admin site login with the staff_login_required
# decorator, which will raise a PermissionDenied exception if a
# logged-in, but non-staff user attempts to access the login page.
admin.site.login = staff_login_required(admin.site.login)

urlpatterns = [
    path('', data_explorer.views.index),
    path('about/', data_explorer.views.about),
    path('step_cap/', data_explorer.views.step_cap),
    path('logout/', data_explorer.views.logout),
    path('uaa_logout/', data_explorer.views.uaa_logout),
    path('safe-mode/', include('frontend.safe_mode')),
    path('healthcheck/', healthcheck),
    path('api/', include('api.urls')),
    path('data-quality-report/', contracts.views.data_quality_report),
    re_path('data-quality-report/(?P<slug>.+)/$',
        contracts.views.data_quality_report_detail),
    path('data-capture/', include('data_capture.urls', namespace='data_capture')),
    path('admin/', include('admin.site.urls')),
    path('styleguide/', include('styleguide.urls', namespace='styleguide')),
    path('robots.txt', robots_txt),
    path('updates/', view_changelog),
    path('auth/', include('uaa_client.urls', namespace='uaa_client')),
    path('session_security/', include('session_security.urls')),
    path('account/', include('user_account.urls', namespace='user_account')),
]

#tests_url = url(r'^tests/$', TemplateView.as_view(template_name='tests.html'),
#                name="tests")

tests_url = path('tests/', TemplateView.as_view(template_name='tests.html'))

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path('admin/doc/', include('django.contrib.admindocs.urls')),
    ] + urlpatterns + [
        path('__debug__/', include('debug_toolbar.urls')),
        re_path('login-sample-user/(?P<username>[A-Za-z0-9_\-]+)$',
            login_sample_user),
        tests_url,
    ]

api_name = 'calc'