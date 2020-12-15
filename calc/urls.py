from django.conf import settings
from django.conf.urls import include, url
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
    url(r'^$', data_explorer.views.index, name='index'),
    url(r'^about/$', data_explorer.views.about, name='about'),
    url(r'^estimating_tool/$', data_explorer.views.estimating_tool, name='estimating_tool'),
    url(r'^step_cap/$', data_explorer.views.step_cap, name='step_cap'),
    url(r'^logout/$', data_explorer.views.logout, name='logout'),
    url(r'^uaa_logout/$', data_explorer.views.uaa_logout, name='uaa_logout'),
    url(r'^safe-mode/', include('frontend.safe_mode', namespace='safe_mode')),
    url(r'^healthcheck/', healthcheck),
    url(r'^api/', include('api.urls')),
    url(r'^data-quality-report/$',
        contracts.views.data_quality_report, name='data_quality_report'),
    url(r'^data-quality-report/(?P<slug>.+)/$',
        contracts.views.data_quality_report_detail, name='data_quality_report_detail'),
    url(r'^data-capture/',
        include('data_capture.urls', namespace='data_capture')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^styleguide/', include('styleguide.urls', namespace='styleguide')),
    url(r'^robots.txt$', robots_txt),
    url(r'^updates/$', view_changelog, name='updates'),
    url(r'^auth/', include('uaa_client.urls', namespace='uaa_client')),
    url(r'session_security/', include('session_security.urls')),
    url(r'^account/', include('user_account.urls', namespace='user_account')),
]

tests_url = url(r'^tests/$', TemplateView.as_view(template_name='tests.html'),
                name="tests")

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    ] + urlpatterns + [
        url(r'^__debug__/', include(debug_toolbar.urls)),
        url(r'^login-sample-user/(?P<username>[A-Za-z0-9_\-]+)$',
            login_sample_user, name='login_sample_user'),
        tests_url,
    ]
