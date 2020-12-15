from django.conf.urls import url, include

from . import (
    views, ajaxform_example, date_example, radio_checkbox_example,
    email_examples, fullpage_example
)


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^docs/$', views.docs, name='docs'),
    url(r'^fullpage-example/' + fullpage_example.REGEX + '$',
        fullpage_example.view, name='fullpage_example'),
    url(r'^ajaxform$', ajaxform_example.view, name='ajaxform'),
    url(r'^date$', date_example.view, name='date'),
    url(r'^radio-checkbox$', radio_checkbox_example.view,
        name='radio-checkbox'),
    url(r'^email/', include(email_examples.urls,
                            namespace='email_examples')),
]
