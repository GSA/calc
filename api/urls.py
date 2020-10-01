from django.conf.urls import url
from django.urls import include, re_path, path

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.documentation import include_docs_urls
from .capability_statement import capability_statement

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
    path('rates/', views.GetRates.as_view()),
    path('rates/csv/', views.GetRatesCSV.as_view()),
    path('search/', views.GetAutocomplete.as_view()),
    path('schedules/', views.ScheduleMetadataList.as_view()),
    path('docs/', include_docs_urls(
        title='CALC API',
        description=views.DOCS_DESCRIPTION,
    )),
    path('capabilitystatement/', views.GetCapabilityStatement.as_view()),
    path('capabilitystatement/url/', views.GetCapabilityStatementUrl.as_view()),
    re_path('swagger(?P<format>\.json|\.yaml)',
        schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path('contract/capability_statement/(?P<contractnumber>[\w-]+)/$',
        capability_statement.get_capability_statment),  # after login
    path('contract/capability_statement/url/(?P<contractnumberlist>[\w,-]+)/$',
        capability_statement.get_bulk_capability_statment),
]

app_name = 'api'
