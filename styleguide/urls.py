from django.conf.urls import url, include
from django.urls import path, include

from . import (
    views, ajaxform_example, date_example, radio_checkbox_example,
    email_examples, fullpage_example
)


urlpatterns = [
    #url(r'^$', views.index, name='index'),
    path('', views.index),
    #url(r'^docs/$', views.docs, name='docs'),
    path('docs/', views.docs),
    
    # @TODO path(r'^fullpage-example/' + fullpage_example.REGEX + '$',
    #    fullpage_example.view, name='fullpage_example'),
    path('fullpage-example/<name>/', fullpage_example.view),
    
    # path(r'^ajaxform$', ajaxform_example.view, name='ajaxform'),
    path('ajaxform', ajaxform_example.view),
    
    #url(r'^date$', date_example.view, name='date'),
    path('date', date_example.view),
    
    # path(r'^radio-checkbox$', radio_checkbox_example.view,
    #     name='radio-checkbox'),
    
    path('radio-checkbox', radio_checkbox_example.view),
    # url(r'^email/', include(email_examples.urls,
    #                         namespace='email_examples')),
    # path('email/', include(email_examples.urls, namespace='email_examples')),
    # @TODO path('email/', include('email_examples.urls')),
]

app_name = 'styleguide'
