import math
import logging
from collections import namedtuple
from typing import Any, Dict  # noqa: F401
from urllib.parse import urlencode

from django.conf import settings
from django.utils.module_loading import import_string
from django.utils import timezone
from django.db import connection, transaction
from django.db.models import Avg, StdDev, Count
from django.contrib.auth.models import User

from contracts.models import Contract
from ..models import SubmittedPriceList
from .vocabulary import Vocabulary, broaden_query


# When comparing labor rates in units of standard deviations from
# the mean, we run into potential problems if our comparables have very
# little variance. (We also potentially run into division by zero errors.)
#
# To rectify this, we'll force standard deviations to have a minimum
# value.
MIN_STDDEV = 1

# FAR 15.404-1(b)(2) lists seven price analysis techniques by which the
# Government can make a fair and reasonable price determination.
#
# Normally, adequate price competition establishes price reasonableness.
# This is the most commonly used technique, as the majority of Government
# procurement actions attract *two*  or more offers that are competing
# independently for award.
DEFAULT_MIN_COMPARABLES = 2

FoundContracts = namedtuple(
    'FoundContracts',
    ['phrase',
     'contracts',
     'count',
     'finder']
)

logger = logging.getLogger('calc')


def find_comparable_contracts(cursor, vocab, labor_category,
                              min_years_experience, education_level,
                              min_count=DEFAULT_MIN_COMPARABLES,
                              cache=None):
    '''
    Attempt to find contracts that are comparable to the given
    criteria. The search starts out as specific as possible but
    gradually broadens until a minimum number of comparables are found.

    If enough comparables are found, a FoundContracts instance is
    returned. Otherwise, None is returned.
    '''

    if cache is None:
        cache = {}

    finders = []

    for classname in settings.PRICE_LIST_ANALYSIS_FINDERS:
        cls = import_string(classname)
        finders.append(cls(
            min_years_experience=min_years_experience,
            education_level=education_level
        ))

    for phrase in broaden_query(cursor, vocab, labor_category, cache,
                                min_count):
        phrase_qs = Contract.objects.all().multi_phrase_search(phrase)
        for finder in finders:
            no_results_key = (
                '{}:no_results'.format(finder.__class__.__name__),
                phrase,
                min_count,
                finder.get_data_explorer_qs_params()
            )
            if no_results_key in cache:
                continue

            contracts = finder.filter_queryset(phrase_qs)
            count = contracts.count()
            if count >= min_count:
                return FoundContracts(
                    phrase=phrase,
                    contracts=contracts,
                    count=count,
                    finder=finder
                )
            else:
                cache[no_results_key] = True
    return None


def get_most_common_edu_levels(qs):
    '''
    Returns a list containing the most common education levels in
    the given QuerySet. The list only has more than one entry in
    the case of ties.
    '''

    results = qs.values('education_level').annotate(
        count=Count('id'),
    ).order_by('-count')
    top_count = results[0]['count']
    return [result['education_level'] for result in results
            if result['count'] == top_count]


def get_data_explorer_url(found_contracts):
    # TODO: Use url mapper to get URL for the data explorer.

    params = (
        ('q', found_contracts.phrase),
    ) + found_contracts.finder.get_data_explorer_qs_params()

    return '/?{}'.format(urlencode(params))


def describe(cursor, vocab, labor_category, min_years_experience,
             education_level, price, severe_stddevs=2,
             min_comparables=DEFAULT_MIN_COMPARABLES,
             cache=None):
    if cache is None:
        cache = {}

    result = {
        'severe': False,
    }  # type: Dict[str, Any]

    fc = find_comparable_contracts(
        cursor,
        vocab,
        labor_category,
        min_years_experience,
        education_level,
        min_count=min_comparables,
        cache=cache
    )

    if fc is not None:
        wage_field = 'current_price'
        stats = fc.contracts.aggregate(
            avg=Avg(wage_field),
            stddev=StdDev(wage_field),
            avg_exp=Avg('min_years_experience'),
        )
        avg = stats['avg']
        stddev = stats['stddev']

        result['avg_exp'] = stats['avg_exp']

        price_delta = abs(price - avg)

        if price_delta > severe_stddevs * stddev:
            result['severe'] = True

        result['count'] = fc.count
        result['avg'] = avg

        if stddev < MIN_STDDEV:
            stddev = MIN_STDDEV

        stddevs = math.ceil(price_delta / stddev)

        result['stddev'] = stddev
        result['stddevs'] = stddevs

        result['most_common_edu_levels'] = get_most_common_edu_levels(
            fc.contracts)

        result['dist_from_avg'] = avg - price if price < avg else price - avg
        result['dist_from_avg_percent'] = (result['dist_from_avg'] / avg) * 100
        result['preposition'] = ('below' if price < avg else 'above')

        result['labor_category'] = fc.phrase
        result['url'] = get_data_explorer_url(fc)
        result['comparable_search_criteria'] = {
            'exp': fc.finder.get_exp_comparable_search_criteria(),
            'edu': fc.finder.get_edu_comparable_search_criteria(),
        }

    return result


def analyze_price_list_row(cursor, vocab, row):
    analysis = describe(
        cursor,
        vocab,
        row.labor_category,
        row.min_years_experience,
        row.education_level,
        float(row.base_year_rate),
    )
    return {
        'analysis': analysis,
        'labor_category': row.labor_category,
        'education_level': row.education_level,
        'min_years_experience': row.min_years_experience,
        'price': float(row.base_year_rate),
    }


def analyze_gleaned_data(gleaned_data):
    print("************core.py gleaned_data ***********")
    print(gleaned_data)

    valid_rows = []

    if gleaned_data and gleaned_data.valid_rows:
        cursor = connection.cursor()
        vocab = Vocabulary.from_db(cursor)
        with transaction.atomic():
            sid = transaction.savepoint()
            fake_user = User.objects.create_user('fake_analysis_user')
            price_list = SubmittedPriceList(
                contract_number='(price list analysis)',
                submitter=fake_user,
                is_small_business=False,
                submitter_id=0,
                escalation_rate=0,
                status_changed_at=timezone.now(),
                status_changed_by_id=0,
            )
            price_list.save()
            gleaned_data.add_to_price_list(price_list)
            cached_rows: Dict[str, Dict] = {}
            cachingCount = 0
            totalCount = 0
            for row in price_list.rows.all():
                key = row.labor_category + row.education_level + str(row.min_years_experience)
                if key in cached_rows:
                    valid_rows.append(cached_rows[key])
                    cachingCount = cachingCount + 1
                    totalCount = totalCount + 1
                    logger.info('Key {} Caching {} total {}'.format(key, cachingCount, totalCount))
                else:
                    processed_raw = analyze_price_list_row(cursor, vocab, row)
                    cached_rows[key] = processed_raw
                    valid_rows.append(processed_raw)
                    totalCount = totalCount + 1
                    logger.info('key {} Caching {} count {}'.format(key, cachingCount, totalCount))
            transaction.savepoint_rollback(sid)

    return valid_rows
