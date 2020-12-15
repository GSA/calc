from unittest import TestCase
from django.test import TestCase as DjangoTestCase, override_settings
from django.db import connection

from calc.tests.common import BaseLoginTestCase
from contracts.mommy_recipes import get_contract_recipe
from contracts.models import Contract
from ..models import SubmittedPriceListRow
from ..analysis.finders import (
    ExactEduAndExpFinder,
    GteEduAndExpFinder,
)
from ..analysis.core import (
    find_comparable_contracts,
    get_most_common_edu_levels,
    describe,
    analyze_price_list_row,
)
from ..analysis.vocabulary import (
    Vocabulary,
    get_best_permutations,
    broaden_query,
)
from ..analysis.export import AnalysisExport, COMPARABLES_NOT_FOUND
from ..management.commands.initgroups import ANALYZE_PRICES_PERMISSION


@override_settings(PRICE_LIST_ANALYSIS_FINDERS=[
    'data_capture.analysis.finders.ExactEduAndExpFinder',
    'data_capture.analysis.finders.GteEduAndExpFinder',
])
class BaseDbTestCase(DjangoTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.contract = get_contract_recipe()
        cls.contract.make(
            labor_category="Engineer of Doom ZZ",
            min_years_experience=5,
            education_level="BA",
            current_price=90
        )
        cls.contract.make(
            labor_category="Engineer ZZ",
            min_years_experience=5,
            education_level="BA",
            current_price=100
        )
        cls.cursor = connection.cursor()
        cls.vocab = Vocabulary.from_db(cls.cursor, min_ndoc=1)


class BaseDescribeTestCase(BaseDbTestCase):
    ROW_WITH_COMPARABLES = dict(
        labor_category='Engineer of Doom ZZ',
        min_years_experience=5,
        education_level='BA',
        severe_stddevs=1,
        min_comparables=1,
        price=89
    )

    ROW_WITHOUT_COMPARABLES = dict(
        labor_category='zzzzzzzzzz',
        min_years_experience=0,
        education_level='AA',
        price=0
    )

    def describe(self, *args, **kwargs):
        return describe(
            self.cursor,
            self.vocab,
            *args,
            **kwargs
        )


class DescribeTests(BaseDescribeTestCase):
    def test_it_works_when_proposed_price_is_way_low(self):
        result = self.describe(**self.ROW_WITH_COMPARABLES)
        self.assertEqual(result, {
            'avg': 90.0,
            'avg_exp': 5.0,
            'count': 1,
            'dist_from_avg': 1.0,
            'dist_from_avg_percent': 1.1111111111111112,
            'most_common_edu_levels': ['BA'],
            'preposition': 'below',
            'comparable_search_criteria': {'edu': 'BA', 'exp': '5-9 years'},
            'labor_category': 'Engineer of Doom ZZ',
            'severe': True,
            'stddev': 1,
            'stddevs': 1,
            'url': '/?q=Engineer+of+Doom+ZZ&min_experience=5'
                   '&max_experience=9&education=BA'
        })

    def test_it_does_not_explode_when_stddev_is_zero(self):
        result = self.describe(
            labor_category='Engineer of Doom ZZ',
            min_years_experience=5,
            education_level='BA',
            severe_stddevs=1,
            min_comparables=1,
            price=90
        )
        self.assertEqual(result, {
            'avg': 90.0,
            'avg_exp': 5.0,
            'count': 1,
            'dist_from_avg': 0.0,
            'dist_from_avg_percent': 0.0,
            'most_common_edu_levels': ['BA'],
            'comparable_search_criteria': {'edu': 'BA', 'exp': '5-9 years'},
            'labor_category': 'Engineer of Doom ZZ',
            'preposition': 'above',
            'severe': False,
            'stddev': 1,
            'stddevs': 0,
            'url': '/?q=Engineer+of+Doom+ZZ&min_experience=5'
                   '&max_experience=9&education=BA',
        })

    def test_returns_empty_description_if_no_comparables_found(self):
        result = self.describe(**self.ROW_WITHOUT_COMPARABLES)
        self.assertEqual(result, {
            'severe': False,
        })


class ExportTests(BaseDescribeTestCase):
    @staticmethod
    def to_spl_row(**describe_kwargs):
        return SubmittedPriceListRow(
            labor_category=describe_kwargs['labor_category'],
            min_years_experience=describe_kwargs['min_years_experience'],
            education_level=describe_kwargs['education_level'],
            base_year_rate=describe_kwargs['price'],
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.setup_rows = False

    def setUp(self):
        if not self.setup_rows:
            self.setup_rows = True
            self.row_without_comparables = self.to_analyzed_row(
                self.to_spl_row(**self.ROW_WITHOUT_COMPARABLES))
            self.row_with_comparables = self.to_analyzed_row(
                self.to_spl_row(**self.ROW_WITH_COMPARABLES))
            self.rows = [
                self.row_without_comparables,
                self.row_with_comparables
            ]

    def to_analyzed_row(self, spl_row):
        return analyze_price_list_row(self.cursor, self.vocab, spl_row)

    def test_to_csv_works(self):
        response = AnalysisExport(self.rows).to_csv()
        self.assertEqual(response['Content-Disposition'],
                         'attachment; filename="analysis.csv"')
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertContains(response, 'Average Price')

    def test_to_xlsx_works(self):
        response = AnalysisExport(self.rows).to_xlsx()
        self.assertEqual(response['Content-Disposition'],
                         'attachment; filename="analysis.xlsx"')
        self.assertEqual(response['Content-Type'],
                         'application/vnd.openxmlformats-'
                         'officedocument.spreadsheetml.sheet')

    def test_exporting_row_without_comparables_works(self):
        _, row = next(AnalysisExport([
            self.row_without_comparables]).to_output_rows())
        self.assertEqual(row.comparables, 0)
        self.assertEqual(row.search_labor_category, COMPARABLES_NOT_FOUND)
        self.assertEqual(row.exp_comparable_search_criteria, '')
        self.assertEqual(row.edu_comparable_search_criteria, '')
        self.assertEqual(row.avg_exp, '')
        self.assertEqual(row.most_common_edu, '')

    def test_exporting_row_with_comparables_works(self):
        _, row = next(AnalysisExport([
            self.row_with_comparables]).to_output_rows())
        self.assertEqual(row.comparables, 2)
        self.assertEqual(row.search_labor_category, 'Engineer of Doom ZZ')
        self.assertEqual(row.exp_comparable_search_criteria, '5-9 years')
        self.assertEqual(row.edu_comparable_search_criteria, 'BA')
        self.assertEqual(row.avg_exp, 5.0)
        self.assertEqual(row.most_common_edu, 'BA')


class GetMostCommonEduLevelsTests(DjangoTestCase):
    def setUp(self):
        self.contract = get_contract_recipe()

    def test_it_reports_decisive_winners(self):
        self.contract.make(education_level='BA')
        self.contract.make(education_level='BA')
        self.contract.make(education_level='AA')
        self.assertEqual(
            get_most_common_edu_levels(Contract.objects.all()),
            ['BA']
        )

    def test_it_reports_ties(self):
        self.contract.make(education_level='BA')
        self.contract.make(education_level='BA')
        self.contract.make(education_level='AA')
        self.contract.make(education_level='AA')
        common_levels = get_most_common_edu_levels(Contract.objects.all())
        self.assertEqual(len(common_levels), 2)
        assert 'BA' in common_levels
        assert 'AA' in common_levels


class BroadenQueryTests(BaseDbTestCase):
    def broaden(self, query, min_count=1):
        return broaden_query(
            self.cursor,
            self.vocab,
            query,
            cache={},
            min_count=min_count,
        )

    def test_first_yields_query_without_stop_words(self):
        self.assertEqual(next(self.broaden('clerical II')), 'clerical')


class FindComparableContractsTests(BaseDbTestCase):
    def find_comparable_contracts(self, *args, **kwargs):
        return find_comparable_contracts(
            self.cursor,
            self.vocab,
            *args,
            **kwargs
        )

    def test_broadening_experience_works(self):
        fc = self.find_comparable_contracts(
            labor_category='Engineer of Doom ZZ',
            min_years_experience=0,
            education_level='BA',
            min_count=1,
        )
        self.assertEqual(fc.phrase, 'Engineer of Doom ZZ')
        self.assertEqual(fc.count, 1)
        self.assertEqual(fc.finder.__class__, GteEduAndExpFinder)

    def test_broadening_education_works(self):
        fc = self.find_comparable_contracts(
            labor_category='Engineer of Doom ZZ',
            min_years_experience=5,
            education_level='AA',
            min_count=1,
        )
        self.assertEqual(fc.phrase, 'Engineer of Doom ZZ')
        self.assertEqual(fc.count, 1)
        self.assertEqual(fc.finder.__class__, GteEduAndExpFinder)

    def test_exact_match_searches_work(self):
        fc = self.find_comparable_contracts(
            labor_category='Engineer of Doom ZZ',
            min_years_experience=5,
            education_level='BA',
            min_count=1,
        )
        self.assertEqual(fc.phrase, 'Engineer of Doom ZZ')
        self.assertEqual(fc.count, 1)
        self.assertEqual(fc.finder.__class__, ExactEduAndExpFinder)

    def test_broadening_labor_category_works(self):
        fc = self.find_comparable_contracts(
            labor_category='Engineer of Doom ZZ',
            min_years_experience=5,
            education_level='BA',
            min_count=2,
        )
        self.assertEqual(fc.phrase, 'Engineer ZZ')
        self.assertEqual(fc.count, 2)
        self.assertEqual(fc.finder.__class__, ExactEduAndExpFinder)

    def test_returns_nothing_if_no_matches_found(self):
        fc = self.find_comparable_contracts(
            labor_category='zzzzzzzzzz',
            min_years_experience=0,
            education_level='AA',
        )
        self.assertEqual(fc, None)


class GteEduAndExpFinderTests(TestCase):
    def test_get_valid_education_levels_works(self):
        finder = GteEduAndExpFinder(1, 'AA')
        self.assertEqual(finder.get_valid_education_levels(),
                         ['AA', 'BA', 'MA', 'PHD'])

    def test_get_data_explorer_qs_params_works(self):
        finder = GteEduAndExpFinder(1, 'MA')
        self.assertEqual(finder.get_data_explorer_qs_params(), (
            ('min_experience', '1'),
            ('education', 'MA,PHD')
        ))


class GetBestPermutationsTests(TestCase):
    def test_min_length_works(self):
        vocab = Vocabulary.from_list([
            'engineer',
            'engineer zz',
        ])

        self.assertEqual(
            get_best_permutations(vocab, ['engineer', 'zz'], min_length=3),
            [('engineer', 'zz'),
             ('engineer',)],
        )

    def test_max_permutations_works(self):
        vocab = Vocabulary.from_list([
            'junior engineer',
            'junior awesome engineer',
            'engineer'
        ])

        self.assertEqual(
            get_best_permutations(vocab, ['junior', 'awesome',
                                          'engineer'], max_permutations=2),
            [('junior', 'awesome', 'engineer'),
             ('junior', 'engineer')]
        )

    def test_restricts_number_of_lexemes(self):
        vocab = Vocabulary.from_list([
            'engineer',
            'engineer zz',
            'administrative assistant zz',
            'administrative assistant zz',
            'senior engineer',
            'project manager',
            'senior specialist',
            'senior generalist',
            'knight',
            'senior knight'
        ])
        words = [
            'engineer',
            'zz',
            'senior',
            'project',
            'manager',
            'assistant',
            'specialist',
            'generalist',
            'knight'
        ]

        result = get_best_permutations(vocab, words, min_length=3,
                                       max_permutations=20)
        """
        Without the restriction on the number of lexemes, the result here
        should be:
        [('zz', 'assistant'), ('engineer', 'zz'), ('engineer', 'senior'),
        ('senior', 'specialist'), ('senior', 'generalist'), ('senior',
        'knight'), ('project', 'manager'), ('senior',), ('engineer',),
        ('assistant',), ('knight',), ('project',), ('manager',),
        ('specialist',), ('generalist',)]
        """

        self.assertEqual(
            result, [
                ('zz', 'assistant'),
                ('engineer', 'zz'),
                ('engineer', 'senior'),
                ('senior', 'specialist'),
                ('senior', 'generalist'),
                ('project', 'manager'),
                ('senior',),
                ('engineer',),
                ('assistant',),
                ('project',),
                ('manager',),
                ('specialist',),
                ('generalist',)
            ]
        )

    def test_it_works(self):
        vocab = Vocabulary.from_list([
            'junior engineer',
            'engineer zz',
            'administrative assistant zz',
            'administrative assistant zz',
            'senior engineer',
            'project manager zz',
        ])
        self.assertEqual(
            get_best_permutations(vocab, ['junior', 'administrative',
                                          'engineer']),
            [('junior', 'engineer'),
             ('engineer',),
             ('administrative',),
             ('junior',)]
        )


class AnalyzeViewTests(BaseLoginTestCase):
    def test_index_nav_logged_out(self):
        response = self.client.get("/")
        self.assertContains(response, 'About CALC')
        self.assertNotContains(response, 'Analyze Prices')
        response = self.client.get("/data-capture/analyze/1")
        self.assertEqual(response.status_code, 302)

    def test_index_nav_logged_in_with_analyze_perms(self):
        super().login(permissions=[ANALYZE_PRICES_PERMISSION])
        response = self.client.get("/")
        self.assertContains(response, 'About CALC')
        self.assertContains(response, 'Analyze prices')
        response = self.client.get("/data-capture/analyze/1")
        self.assertEqual(response.status_code, 200)

    def test_index_nav_logged_in_without_analyze_perms(self):
        super().login(permissions=[])
        response = self.client.get("/")
        self.assertContains(response, 'About CALC')
        self.assertNotContains(response, 'Analyze prices')
        response = self.client.get("/data-capture/analyze/1")
        self.assertEqual(response.status_code, 403)
