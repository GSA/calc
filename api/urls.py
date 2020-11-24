from django.conf.urls import url
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.documentation import include_docs_urls
from .capability_statement import capability_statement
from .bls_pet import bls_pet

from api import views

schema_view = get_schema_view(
    openapi.Info(
        title="CALC API",
        default_version='v2',
        description="CALC API DOCUMENTATION",
        contact=openapi.Contact(email="calc@gsa.gov"),
    ),
    url=views.Util.getHostName(views.Util),
    public=True,
    generator_class=views.CustomOpenAPISchemaGenerator,
)

urlpatterns = [
    url(r'^rates/$', views.GetRates.as_view()),
    url(r'^rates/csv/$', views.GetRatesCSV.as_view()),
    url(r'^search/$', views.GetAutocomplete.as_view()),
    url(r'^schedules/$', views.ScheduleMetadataList.as_view()),
    url(r'^docs/', include_docs_urls(
        title='CALC API',
        description=views.DOCS_DESCRIPTION,
    )),
    url(r'^bls_pet/autocomplete/(?P<search_term>[\w,-]+)/$', views.GetBLSAutocomplete.as_view()),
    url(r'^bls_pet/getprice', views.GetBLSGetPrice.as_view()),


    url(r'^capabilitystatement/$', views.GetCapabilityStatement.as_view()),
    url(r'^capabilitystatement/url/$', views.GetCapabilityStatementUrl.as_view()),
    url(r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^contract/capability_statement/(?P<contractnumber>[\w-]+)/$',
        capability_statement.get_capability_statment),  # after login
    url(r'^contract/capability_statement/url/(?P<contractnumberlist>[\w,-]+)/$',
        capability_statement.get_bulk_capability_statment),

    # url(r'^bls_pet/autocomplte/(?P<search_type>[\w-]+)/$',bls_pet.autocomplete),  # after login
]
