#from django.conf.urls import include, url
from django.urls import include, re_path, path

from .views import (price_list_upload, bulk_upload, price_lists,
                    price_list_replace, price_list_analyze, capability_statement)

urlpatterns = [
    # url(r'^tutorial$', price_list_upload.tutorial, name='tutorial'),
    path('tutorial', include('price_list_upload.tutorial')),

    path('step/', include('price_list_upload.steps.urls')),

    path('step/3/errors$', price_list_upload.step_3_errors),

    path('bulk/region-10/step/', include('bulk_upload.steps.urls')),
    path('price-lists', price_lists.list_price_lists),
    re_path('price-lists/(?P<id>[0-9]+)$', price_lists.price_list_details),

    re_path('price-lists/(?P<id>[0-9]+)/replace/step/',
        include(price_list_replace.steps.urls)),
    re_path('price-lists/(?P<id>[0-9]+)/replace/step/1/errors$',
        price_list_replace.replace_step_1_errors),

    path('analyze/', include('price_list_analyze.steps.urls')),

    path('capability_statement/', capability_statement.add_capability_statment),


    path('analyze/2/errors', price_list_analyze.analyze_step_2_errors),
    path('analyze/export', price_list_analyze.export_analysis),
]

api_name = 'data_capture'
