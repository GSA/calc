import bleach
import csv
from decimal import Decimal
from textwrap import dedent

from django.http import HttpResponse
from django.db.models import Avg, Max, Min, Count, StdDev
from django.utils.safestring import SafeString
from urllib.parse import urlparse

from markdown import markdown
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.schemas import AutoSchema
from rest_framework.compat import coreapi, coreschema
from django.utils.html import strip_tags
from rest_framework import generics

from api.pagination import ContractPagination
from api.serializers import ContractSerializer, ScheduleMetadataSerializer
from api.utils import get_histogram
from contracts.models import Contract, EDUCATION_CHOICES, ScheduleMetadata
from calc.utils import humanlist, backtickify
from drf_yasg.generators import OpenAPISchemaGenerator

from django.conf import settings
from django.http import FileResponse
from botocore.exceptions import ClientError
from django.http import JsonResponse
from data_capture.models import capability_statement as conSta
# from django.shortcuts import redirect
import boto3
from django.db.models import Q

#For BLS PET
from data_capture.models import bls_data,bls_lcat,bls_pricing,bls_occupation_lcat_mapping,bls_state,bls_state_city_mapping,bls_occs


DOCS_DESCRIPTION = dedent("""
CALC's back-end exposes a public API for its labor rates data.
This API is used by CALC's front-end Data Explorer application,
and can also be accessed by any third-party application over
the public internet.

For more developer documentation on CALC, please visit
[/docs/](/docs/).
""")

SIMPLE_QUERYARG_TYPE_MAP = {
    int: coreschema.Integer,
    str: coreschema.String,
}

ALL_CONTRACT_FIELDS = ContractSerializer.Meta.fields

SORTABLE_CONTRACT_FIELDS = list(set(
    ContractSerializer.Meta.fields
).intersection(set([f.name for f in Contract._meta.fields if f.db_index])))


def queryarg(name, _type, description):
    '''
    A simple helper method to generate a coreapi field out of a
    less verbose syntax.
    '''

    html_desc = SafeString(markdown(dedent(description)))

    return coreapi.Field(
        name,
        location="query",
        schema=SIMPLE_QUERYARG_TYPE_MAP[_type](
            description=html_desc,
        )
    )


Q_QUERYARG = queryarg("q", str, "Keywords to search by.")

GET_CONTRACTS_QUERYARGS = [
    Q_QUERYARG,
    queryarg(
        "experience_range",
        str,
        """
        Filter by a range of years of experience, e.g. `5-10`.
        This is a convenient alternative to separately
        specifying `min_experience` and `max_experience`.
        """
    ),
    queryarg(
        "min_experience",
        int,
        "Filter by minimum years of experience."
    ),
    queryarg(
        "max_experience",
        int,
        "Filter by maximum years of experience."
    ),
    queryarg(
        "min_education",
        str,
        "Filter by a minimum level of education:\n\n" + '\n'.join([
            f"* `{code}` = {desc}"
            for code, desc in EDUCATION_CHOICES
        ])
    ),
    queryarg(
        "schedule",
        str,
        """
        Filter by GSA schedule. See [/api/schedules/](/api/schedules/)
        for a list of valid values.
        """,
    ),
    queryarg(
        "sin",
        str,
        """
        Filter by SIN number. See [/api/schedules/](/api/schedules/)
        for a list of example values.

        Note that due to the current state of data, not all
        results may be returned.  For more details, see
        [#1033](https://github.com/18F/calc/issues/1033).
        """,
    ),
    queryarg(
        "site",
        str,
        """
        Filter by worksite. Can be `customer`, `contractor`,
        or `both`.
        """
    ),
    queryarg(
        "business_size",
        str,
        """
        Filter by business size: `s` for small business, or
        `o` for other than small business.
        """
    ),
    queryarg(
        "price",
        int,
        "Filter by exact price."
    ),
    queryarg(
        "price__gte",
        int,
        "Price must be greater than or equal to this integer."
    ),
    queryarg(
        "price__lte",
        int,
        "Price must be less than or equal to this integer."
    ),
    queryarg(
        "sort",
        str,
        f"""
        Comma-separated list of columns to sort on.
        Defaults to the field used for pricing.

        Sortable columns include
        {humanlist(backtickify(SORTABLE_CONTRACT_FIELDS))}.
        """
    ),
    queryarg(
        "query_type",
        str,
        """
        Defines how the user's keyword search should work.
        Can be `match_all` (default), `match_phrase`, or `match_exact`.
        """
    ),
    queryarg(
        "exclude",
        str,
        "Comma-separated list of ids to exclude from the search results."
    )
]


def get_contracts_queryset(request_params, wage_field):
    """
    Filters and returns contracts based on query params

    Args:
        request_params (dict): the request query parameters, corresponding
            to GET_CONTRACTS_QUERYARGS above.
        wage_field (str): the name of the field currently being used for
            wage calculations and sorting

    Returns:
        QuerySet: a filtered and sorted QuerySet to retrieve Contract objects
    """

    query = request_params.get('q', None)
    # Ideally we'd go ahead and return a plain queryset here if there is
    # no query to avoid doing extra work, but before we can do that
    # we'll have to ensure filtering fields can't do anything in the absence
    # of a query or else Very Strange Things happen.

    # Since our query can be multi-phrase, leave the original queryset alone.
    # Instead, start with an empty queryset, then find matching subsets
    # in the original and chain them together.
    isSecondaryFilter = False
    if query:
        queryArray = query.split("|")
        if len(queryArray) > 1:
            isSecondaryFilter = True

        query = queryArray[0]
        query_type = request_params.get('query_type', 'match_all')
        query_by = request_params.get('query_by', None)
        contracts = Contract.objects.all().multi_phrase_search(
            query.strip(), query_by, query_type)
    else:  # no query, so start with full query set
        contracts = Contract.objects.all()

    if isSecondaryFilter:
        if queryArray[1] != "":
            secondryFilter = queryArray[1]
            secondryFilterArr = secondryFilter.split(',')
            queryFilters = Q()
            for filter in secondryFilterArr:
                if filter != "":
                    filter = filter.strip()
                    queryFilters = queryFilters | Q(keywords__icontains=filter) | \
                        Q(certifications__icontains=filter) | \
                        Q(description__icontains=filter)
            contracts = contracts.filter(queryFilters)

    # Exclude records w/o rates for the selected contract period.
    # Additional price filtering is already in the CurrentContractManager
    contracts = contracts.exclude(**{wage_field + '__isnull': True})

    exclude = request_params.getlist('exclude')
    if exclude:
        # getlist only works for key=val&key=val2, not for key=val1,val2
        # this is safe because any non-integer value in the request params
        # wouldn't match id__in anyway.

        # TO-DO: take a list of phrases, pass them through
        # `clean_search` and then exclude those phrases
        exclude = exclude[0].split(',')
        contracts = contracts.exclude(id__in=exclude)

    # *** EXPERIENCE ***
    min_experience = request_params.get('min_experience', None)
    max_experience = request_params.get('max_experience', None)
    experience_range = request_params.get('experience_range', None)
    if experience_range:
        years = experience_range.split(',')
        min_experience = years[0]
        if len(years) > 1:
            max_experience = years[1]
    # Ensure the input matches expected numeric format to avoid injections
    if min_experience and min_experience.isdigit():
        contracts = contracts.filter(min_years_experience__gte=min_experience)

    if max_experience and max_experience.isdigit():
        contracts = contracts.filter(min_years_experience__lte=max_experience)

    # *** EDUCATION ***
    ed_levels = [x[0] for x in EDUCATION_CHOICES]
    min_education = request_params.get('min_education', None)
    if min_education:
        min_level = ed_levels.index(min_education)
        if min_level:  # The submitted value matched a choice and wasn't weird.
            contracts = contracts.filter(education_level__in=ed_levels[min_level:])

    education = request_params.get('education', None)
    if education:
        # Find submitted levels that are within our group of accepted values
        degrees = [value for value in education.split(',') if value in ed_levels]
        if degrees:
            contracts = contracts.filter(education_level__in=degrees)

    schedule = request_params.get('schedule', None)
    if schedule:
        schedule = bleach.clean(schedule)
        contracts = contracts.filter(schedule__iexact=schedule)

    site = request_params.get('site', None)
    if site:
        site = bleach.clean(site)
        contracts = contracts.filter(contractor_site__icontains=site)

    business_size = request_params.get('business_size', None)
    if business_size and business_size in ('s', 'o'):
        if business_size == 's':
            contracts = contracts.filter(business_size__istartswith='s')
        else:
            contracts = contracts.filter(business_size__istartswith='o')

    # WE NEED TO DOUBLE CHECK SIN AND PRICE.
    # THEY DO NOT APPEAR TO BE ON THE SEARCH PAGE.
    sin = request_params.get('sin', None)
    if sin:
        contracts = contracts.filter(sin__icontains=sin)

    sin_number = request_params.get('sinNumber', None)
    if sin_number:
        contracts = contracts.filter(sin__icontains=sin_number)

    security_clearance = request_params.get('securityClearance', None)
    if security_clearance:
        contracts = contracts.filter(security_clearance__icontains=security_clearance)
    print(contracts)
    price = request_params.get('price', None)
    price__gte = request_params.get('price__gte')
    price__lte = request_params.get('price__lte')
    if price:
        contracts = contracts.filter(**{wage_field + '__exact': price})
    else:
        if price__gte:
            contracts = contracts.filter(**{wage_field + '__gte': price__gte})
        if price__lte:
            contracts = contracts.filter(**{wage_field + '__lte': price__lte})

    # get any sorting params and sort by them.
    sort = request_params.get('sort', wage_field).split(',')
    for field in sort:
        if field.startswith('-'):
            field = field[1:]
        if field not in ALL_CONTRACT_FIELDS:
            stripped = strip_tags(field)
            clean_field = bleach.clean(stripped, tags=[], strip=True)
            raise serializers.ValidationError(f'"{clean_field}" is not a valid field to sort on')
        if field not in SORTABLE_CONTRACT_FIELDS:
            stripped = strip_tags(field)
            clean_field = bleach.clean(stripped, tags=[], strip=True)
            raise serializers.ValidationError(f'Unable to sort on the field "{clean_field}"')

    return contracts.order_by(*sort)


def quantize(num, precision=2):
    if num is None:
        return None
    return Decimal(num).quantize(Decimal(10) ** -precision)


class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, *args, **kwargs):
        schema = super().get_schema(*args, **kwargs)
        schema.basePath = Util.getApiBasePath(self)
        return schema


class Util:
    def getHostName(self):
        data = urlparse(settings.API_HOST)
        host = ''
        if settings.API_HOST == '/api/':
            host = 'http://localhost:8000/'
        else:
            host = data.scheme + '://' + data.netloc
        return host

    def getApiBasePath(self):
        data = urlparse(settings.API_HOST)
        basePath = ''
        if settings.API_HOST == '/api/':
            basePath = '/api/'
        else:
            basePath = data.path
        return basePath


class GetRates(APIView):
    """
    Get detailed information about all labor rates that match a search query.

    The JSON response contains the following keys:

    * `next` is a URL that points to the next page of results, or
    `null` if no additional pages are available.
    * `previous` is a URL that points to the previous page of
    results, or `null` if no previous pages are available.
    * `results` is an array containing the results for the
    current page. Each item in the array contains the following keys:
        * `id` is the internal ID of the rate in the CALC database.
            This can be passed to the `exclude` query parameter to
            exclude individual rates from search results.
        * `idv_piid` is the contract number of the contract that
            contains the labor rate.
        * `vendor_name` is the name of the vendor that the
            labor rate's contract is under.
        * `education_level` is the minimum level of education
            for the labor rate.
        * `min_years_experience` is the minimum years of experience
            for the labor rate.
        * `hourly_rate_year1`, `current_price`, `next_year_price`,
            and `second_year_price` contain pricing information for
            the labor rate.
        * `schedule` is the schedule the labor rate is under. See
            [/api/schedules/](/api/schedules/) for a list of valid values.
        * `sin` describes the special item numbers (SINs) the labor
            rate is under. See
            [#1033](https://github.com/18F/calc/issues/1033) for
            details on some limitations.
        * `contractor_site` is the worksite of the labor rate.
        * `business_size` is the business size of the vendor
            offering the labor rate.

    Additionally, the response contains aggregate details about
    the distribution of the search results, across all pages:

    * `count` is the total number rates.
    * `average` is the average price of the rates.
    * `minimum` is the minimum price of the rates.
    * `maximum` is the maximum price of the rates.
    * `first_standard_deviation` is the first standard deviation
      of the rates.
    * `wage_histogram` is an array that contains an object for
      each bin in the histogram (the number of bins can be
      specified via the `histogram` query parameter):
        * `min` is the minimum price of the bin.
        * `max` is the maximum price of the bin.
        * `count` is the number of prices in the bin.
    """

    # The AutoSchema will introspect this to ultimately generate
    # documentation about our pagination query args.
    pagination_class = ContractPagination

    schema = AutoSchema(
        manual_fields=[
            queryarg(
                "contract-year",
                int,
                """
                Return price for the given contract year (1 or 2).
                Defaults to the current year pricing.
                """
            ),
            queryarg(
                "histogram",
                int,
                """
                Number of bins to divide a wage histogram into.
                If not provided, no histogram data will be returned.
                """
            ),
        ] + GET_CONTRACTS_QUERYARGS
    )

    def get(self, request):
        bins = request.query_params.get('histogram', None)

        """
        wage_field determines prices for a given year:
        This year, next year, or the year after.
        Relies on indexing a list, which may be less reliable than a tuple.

        This is used both here in get() and downstream in get_query_set(),
        so we have to pass it through.
        """
        possible_wage_fields = ['current_price', 'next_year_price', 'second_year_price']
        year = request.query_params.get('contract-year', 0)
        wage_field = possible_wage_fields[int(year)]
        contracts_all = self.get_queryset(request.query_params, wage_field)

        stats = contracts_all.aggregate(
            Min(wage_field), Max(wage_field),
            Avg(wage_field), StdDev(wage_field))

        page_stats = {
            'minimum': stats[wage_field + '__min'],
            'maximum': stats[wage_field + '__max'],
            'average': quantize(stats[wage_field + '__avg']),
            'first_standard_deviation': quantize(
                stats[wage_field + '__stddev']
            )
        }

        if bins and bins.isnumeric():
            values = contracts_all.values_list(wage_field, flat=True)
            page_stats['wage_histogram'] = get_histogram(values, int(bins))

        pagination = self.pagination_class(page_stats)
        results = pagination.paginate_queryset(contracts_all, request)
        serializer = ContractSerializer(results, many=True)
        return pagination.get_paginated_response(serializer.data)

    def get_queryset(self, request, wage_field):
        return get_contracts_queryset(request, wage_field)


class ScheduleMetadataList(generics.ListAPIView):
    """
    Returns an array of objects representing metadata about
    Schedules offered by CALC. Each object contains the following keys:

    * `schedule` is the identifier for the schedule as it appears in
      other CALC API endpoints, such as [/api/rates/](/api/rates/).
    * `full_name` is the full name of the schedule as it should appear
      to end users.
    * `sin` is the SIN number of the schedule, if one exists.
    """

    queryset = ScheduleMetadata.objects.all()
    serializer_class = ScheduleMetadataSerializer


class GetRatesCSV(APIView):
    """
    Returns a CSV of matched records and selected search and filter options.

    Note that the first two rows actually contain metadata about the requested
    search and filter options. The subsequent rows contain the
    matched records.
    """

    schema = AutoSchema(
        manual_fields=GET_CONTRACTS_QUERYARGS
    )

    def get(self, request, format=None):
        wage_field = 'current_price'
        contracts_all = get_contracts_queryset(request.GET, wage_field)

        q = request.query_params.get('q', 'None')

        # If the query starts with special chars that could be interpreted
        # as parts of a formula by Excel, then prefix the query with
        # an apostrophe so that Excel instead treats it as plain text.
        # See https://issues.apache.org/jira/browse/CSV-199
        # for more information.
        if q.startswith(('@', '-', '+', '=', '|', '%')):
            q = "'" + q

        min_education = request.query_params.get(
            'min_education', 'None Specified')
        min_experience = request.query_params.get(
            'min_experience', 'None Specified')
        site = request.query_params.get('site', 'None Specified')
        business_size = request.query_params.get(
            'business_size', 'None Specified')
        business_size_map = {
            'o': 'other than small',
            's': 'small business'
        }
        business_size_set = business_size_map.get(business_size)
        if business_size_set:
            business_size = business_size_set

        response = HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = ('attachment; '
                                           'filename="pricing_results.csv"')
        writer = csv.writer(response)
        writer.writerow(("Search Query", "Minimum Education Level",
                         "Minimum Years Experience", "Worksite",
                         "Business Size", "", "", "", "", "", "", "", "", ""))
        writer.writerow((q, min_education, min_experience, site,
                         business_size, "", "", "", "", "", "", "", "", ""))
        writer.writerow(("Contract #", "Business Size", "Schedule", "Site",
                         "Begin Date", "End Date", "SIN", "Vendor Name",
                         "Labor Category", "education Level",
                         "Minimum Years Experience",
                         "Current Year Labor Price", "Next Year Labor Price",
                         "Second Year Labor Price"))

        for c in contracts_all:
            writer.writerow((c.idv_piid, c.get_readable_business_size(),
                             c.schedule, c.contractor_site, c.contract_start,
                             c.contract_end, c.sin, c.vendor_name,
                             c.labor_category, c.get_education_level_display(),
                             c.min_years_experience, c.current_price,
                             c.next_year_price, c.second_year_price))

        return response


class GetAutocomplete(APIView):
    """
    Return autocomplete suggestions for a given query.

    The JSON response is an array containing objects
    with the following keys:

    * `labor_category` is the name of a labor category that
      matches your query.

    * `count` is the number of records with the labor category.
    """

    schema = AutoSchema(
        manual_fields=[
            Q_QUERYARG,
            queryarg(
                "query_type",
                str,
                """
                Defines how the search query should work.
                Can be `match_all` (default) or `match_phrase`.
                """
            )
        ]
    )

    MAX_RESULTS = 20

    def get(self, request, format=None):
        q = request.query_params.get('q', False)
        query_type = request.query_params.get('query_type', 'match_all')
        query_by = request.query_params.get('query_by', None)

        if q:
            data = Contract.objects.all().multi_phrase_search(
                q, query_by, query_type)

            data = data.values('_normalized_labor_category').annotate(
                count=Count('_normalized_labor_category')).order_by('-count')

            # limit data to MAX_RESULTS
            data = data[:self.MAX_RESULTS]

            data = [
                {'labor_category': d['_normalized_labor_category'],
                 'count': d['count']}
                for d in data
            ]
            return Response(data)
        else:
            return Response([])


class GetCapabilityStatement(APIView):
    """
    Returns PDF or Docx for the selected contract.

    """

    schema = AutoSchema(
        manual_fields=[
            queryarg(
                "contract_number",
                str,
                """
                Return capability statement per contract.
                """
            ),
            # queryarg(
            #     "url",
            #     str,
            #     """
            #     Return url of the submitted contract.
            #     """
            # ),
        ]
    )

    def check(self, s3, bucket, key):
        try:
            s3.head_object(Bucket=bucket, Key=key)
        except ClientError as e:
            return int(e.response['Error']['Code']) != 404
        return True

    def get(self, request, format=None):
        req = request.GET
        required_data = req['contract_number']
        conIns = conSta.objects.filter(contract_number=str(required_data))
        if conIns:
            url = conIns[0].url  # getting url from db
            # response = JsonResponse({'Error': '1', 'ErrorMessage': url})
            # return response
            return JsonResponse({'Error': '1', 'ErrorMessage': url})
        else:
            AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
            AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
            AWS_REGION = settings.AWS_REGION
            AWS_BUCKET = settings.AWS_STORAGE_BUCKET_NAME
            s3 = boto3.client('s3', AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        try:
            s3bucket = s3.list_objects_v2(Bucket=AWS_BUCKET)
        except ClientError as e:
            response = JsonResponse({'Error': '1', 'ErrorMessage': 'Invalid AWS Credentials'})
            return response
        # Only return the contents if we found some keys
        if s3bucket['KeyCount'] > 0:
            all_objects = s3bucket['Contents']
        else:
            response = JsonResponse({'Error': '1', 'ErrorMessage': 'No Files Found on bucket'})
            return response

        objectsNeed = []
        date_arr = []
        for obj in all_objects:
            obj_name = str(obj["Key"]).split('.')
            if required_data == obj_name[0]:
                objectsNeed.append({obj['LastModified']: obj['Key']})
                date_arr.append(obj['LastModified'])

        if len(date_arr) == 0:  # If invalid contract number given
            response = JsonResponse({'Error': '1', 'ErrorMessage': 'Invalid Contract Number'})
            return response
        else:
            latest_update = max(date_arr)
            index_of_latest_update = date_arr.index(latest_update)
            latest_file = str(objectsNeed[index_of_latest_update].get(
                              date_arr[index_of_latest_update]))

            if self.check(s3, AWS_BUCKET, latest_file):
                try:
                    file = s3.get_object(Bucket=AWS_BUCKET, Key=latest_file)
                    ext_array = latest_file.split('.')
                    response = FileResponse(file['Body'], content_type='application/' +
                                            ext_array[1])
                    response['Content-Disposition'] = 'attachment; filename="' + latest_file + '"'
                    return response
                except FileNotFoundError:
                    response = JsonResponse({'Error': '1',
                                            'ErrorMessage': 'Error While Downloading'})
        return response


class GetBLSGetPrice(APIView):
    def post(slef,request):
        data = request.data
        occupationCode = data['occupation_code']
        lcatId = data['lcat_id']
        areaId = data['area_id']

        lcatTitleInstance = bls_lcat.objects.get(id=lcatId)
        stateCityMappingInstance = bls_state_city_mapping.objects.get(id=areaId)
        blsPriceInstance = bls_pricing.objects.filter(
            occ_code = occupationCode,
            # lcat_id = lcatTitleInstance,
            area_code = stateCityMappingInstance
        )
        result = []
        if blsPriceInstance:
            result = [{
                'h_mean' : price.h_mean,
                'h_median' : price.h_median,
                'h_pct10' : price.h_pct10,
                'h_pct25' : price.h_pct25,
                'h_pct50' : price.h_pct50,                                                                                                             
                'h_pct75' : price.h_pct75,
                'h_pct90' : price.h_pct90,
            } for price in blsPriceInstance]
        return JsonResponse({'Error':0,'Error_Message':'','data':result})

class GetBLSAutocomplete(APIView):
    def get(self,request,search_term):
        if search_term == 'occupation':
            try:
                blsData = bls_occs.objects.order_by('occupation').values('occupation_code','occupation').distinct()
                if blsData:
                    result = [{
                        "code":n['occupation_code'],
                        "occupation":n['occupation']
                    } for n in blsData]
                    return JsonResponse({'Error': 0,'ErrorMessage': '','data':result})
                else:
                    return JsonResponse({'Error': 1,'ErrorMessage': 'Something Went Wrong','data':[]})
            except:
                return JsonResponse({'Error': 1,'ErrorMessage': 'Something Went Wrong','data':[]})
        elif search_term == 'state':
            try:
                blsState = bls_state.objects.all().order_by('state')
                if blsState:
                    result = [{
                        "id":n.id,
                        "state":n.state,
                        "code":n.state_code
                    } for n in blsState]
                    return JsonResponse({'Error': 0,'ErrorMessage': '','data':result})
                else:
                    return JsonResponse({'Error': 1,'ErrorMessage': 'Something Went Wrong','data':[]})
            except:
                return JsonResponse({'Error': 1,'ErrorMessage': 'Something Went Wrong','data':[]})




    def post(self,request,search_term):
        if search_term == 'lcat':
            data = request.data
            occupationID = data['occ_id']
            blsLcatRef = bls_occupation_lcat_mapping.objects.filter(occupation_code = occupationID)
            result = [{
                    'lcat_id':0,
                    'lcat_title':'ancillary'
                }]
            eandqlevels = [
                {
                "value": "JR", "description": "WL1"
                }, {
                "value": "JY", "description": "WL2"
                }, {
                "value": "SR", "description": "WL3"
                }, {
                "value": "XP", "description": "WL4"
                },
            ]
            if len(blsLcatRef) > 0:
                result = []
                for n in blsLcatRef:
                    if not n.lcat.lcat_title == "nan":
                        node = {
                            'lcat_id':n.lcat.id,
                            'lcat_title':n.lcat.lcat_title
                        }
                        result.append(node)
                eandqlevels = [
                    {
                    "value": "JR", "description": "Junior"
                    }, {
                    "value": "JY", "description": "Journeyman"
                    }, {
                    "value": "SR", "description": "Senior"
                    }, {
                    "value": "XP", "description": "SME"
                    },
                ]
            finalResult = {
                'lcat_details':result,
                'eandqlevels':eandqlevels
            }
            return JsonResponse({'Error': 0,'ErrorMessage': '','data':finalResult})
        elif search_term == 'area':
            data = request.data
            stateCode = data['state_code']
            blsStateIns = bls_state.objects.filter(state_code = stateCode)
            result = []
            if blsStateIns:
                cities = bls_state_city_mapping.objects.filter(state = blsStateIns[0])
                result = [{
                    'id':n.id,
                    'city':n.city
                }for n in cities]
            return JsonResponse({'Error': 0,'ErrorMessage': '','data':result})





class GetCapabilityStatementUrl(APIView):
    """
    Returns PDF or Docx for the selected contract.

    """

    schema = AutoSchema(
        manual_fields=[
            queryarg(
                "contract_number",
                str,
                """
                Return capability statement url for multiple contracts.
                """
            ),
        ]
    )

    def check(self, s3, bucket, key):
        try:
            s3.head_object(Bucket=bucket, Key=key)
        except ClientError as e:
            return int(e.response['Error']['Code']) != 404
        return True

    def get(self, request, format=None):
        AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
        AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
        AWS_REGION = settings.AWS_REGION
        AWS_BUCKET = settings.AWS_STORAGE_BUCKET_NAME
        s3 = boto3.client('s3', AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        try:
            s3bucket = s3.list_objects_v2(Bucket=AWS_BUCKET)
        except ClientError as e:
            response = JsonResponse({'Error': '1', 'ErrorMessage': 'Invalid AWS Credentials'})
            return response

        if s3bucket['KeyCount'] > 0:
            all_objects = s3bucket['Contents']
        else:
            response = JsonResponse({'Error': '1', 'ErrorMessage': 'No Files Found on bucket'})
            return response
        req = request.GET
        contractnumberlist = req['contract_number']
        contractnumber_array = contractnumberlist.split(',')
        # To avoid repeteating in contract number
        contractnumber_array = list(set(contractnumber_array))
        data = {}
        for con in contractnumber_array:
            conIns = conSta.objects.filter(contract_number=str(con))
            if conIns:
                url = conIns[0].url  # getting url from db
            else:
                objectsNeed = []
                date_arr = []
                for obj in all_objects:
                    obj_name = str(obj["Key"]).split('.')
                    if str(con) == obj_name[0]:
                        objectsNeed.append({obj['LastModified']: obj['Key']})
                        date_arr.append(obj['LastModified'])

                if len(date_arr) == 0:  # If invalid contract number given
                    url = "Not Available"
                else:
                    latest_update = max(date_arr)
                    index_of_latest_update = date_arr.index(latest_update)
                    latest_file = str(objectsNeed[index_of_latest_update].get(
                                      date_arr[index_of_latest_update]))

                    url = s3.generate_presigned_url(
                        ClientMethod='get_object',
                        Params={
                            'Bucket': AWS_BUCKET,
                            'Key': latest_file
                        }
                    )
            data[con] = url
        response = JsonResponse(data)
        return response
