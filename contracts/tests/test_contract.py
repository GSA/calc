import datetime
from unittest.mock import patch
from decimal import Decimal
from itertools import cycle

from django.db import connection
from django.test import TestCase, SimpleTestCase
from contracts.mommy_recipes import get_contract_recipe

from ..models import Contract, CashField


_normalize = Contract.normalize_labor_category


class CashFieldTests(SimpleTestCase):
    def test_value_error_raised_on_invalid_decimal_places(self):
        with self.assertRaisesRegexp(ValueError, r'must have exactly 2'):
            CashField(max_digits=10, decimal_places=4)

    def test_to_python_returns_none_when_value_is_none(self):
        c = CashField(max_digits=10, decimal_places=2)
        self.assertEqual(c.to_python(None), None)

    def test_to_python_returns_decimal_when_value_is_float(self):
        c = CashField(max_digits=10, decimal_places=2)
        self.assertEqual(c.to_python(1.0 / 3), Decimal('0.33'))

    def test_to_python_rounds_decimals(self):
        c = CashField(max_digits=10, decimal_places=2)
        self.assertEqual(c.to_python(Decimal('0.336')), Decimal('0.34'))
        self.assertEqual(c.to_python(Decimal('0.334')), Decimal('0.33'))

    def test_clean_calls_to_python(self):
        # This is really a test to ensure that Django is working
        # the way we think it is.
        c = CashField(max_digits=10, decimal_places=2)
        self.assertEqual(c.clean(1.0 / 3, None), Decimal('0.33'))


class NormalizeLaborCategoryTests(SimpleTestCase):
    def test_abbr_with_period(self):
        self.assertEqual(_normalize('jr. person'), 'junior person')

    def test_abbr_without_period(self):
        self.assertEqual(_normalize('jr person'), 'junior person')

    def test_abbr_at_end(self):
        self.assertEqual(_normalize('person jr.'), 'person junior')

    def test_abbr_in_middle(self):
        self.assertEqual(_normalize('person jr. ham'), 'person junior ham')

    def test_abbr_uppercase(self):
        self.assertEqual(_normalize('JR. PERSON'), 'junior person')


class ContractTestCase(TestCase):
    def make_contract_with_rates(self, **kwargs):
        final_kwargs = dict(
            hourly_rate_year1=100.00,
            hourly_rate_year2=102.20,
            hourly_rate_year3=103.30,
            hourly_rate_year4=104.40,
            hourly_rate_year5=105.50)
        final_kwargs.update(kwargs)
        return get_contract_recipe().make(**final_kwargs)

    def test_bulk_update_normalized_labor_categories_works(self):
        update = Contract.objects.bulk_update_normalized_labor_categories
        c1 = get_contract_recipe().make(labor_category='foo')
        c2 = get_contract_recipe().make(labor_category='bar')

        self.assertEqual(update(), 0)

        with patch.object(Contract, 'normalize_labor_category',
                          lambda self, val: 'lol ' + val):
            self.assertEqual(update(), 2)

        c1.refresh_from_db()
        c2.refresh_from_db()
        self.assertEqual(c1._normalized_labor_category, 'lol foo')
        self.assertEqual(c2._normalized_labor_category, 'lol bar')

        results = Contract.objects.all().multi_phrase_search('lol foo')
        self.assertEqual([r.labor_category for r in results], ['foo'])

    def test_update_normalized_labor_category_returns_bool(self):
        c = get_contract_recipe().prepare(labor_category='jr person')
        self.assertTrue(c.update_normalized_labor_category())
        self.assertFalse(c.update_normalized_labor_category())

    def test_bulk_create_updates_search_index(self):
        c1 = get_contract_recipe().prepare(labor_category='jr person')
        c2 = get_contract_recipe().prepare(labor_category='engineer')
        Contract.objects.bulk_create([c1, c2])

        results = Contract.objects.all().multi_phrase_search('person')
        self.assertEqual([r.labor_category for r in results], ['jr person'])

    def test_bulk_create_updates_normalized_labor_category(self):
        c = get_contract_recipe().prepare(labor_category='jr person')
        self.assertEqual(c._normalized_labor_category, '')
        Contract.objects.bulk_create([c])

        c = Contract.objects.all()[0]
        self.assertEqual(c._normalized_labor_category, 'junior person')

    def test_readable_business_size(self):
        business_sizes = ('O', 'S')
        contract1, contract2 = get_contract_recipe().make(
            _quantity=2, business_size=cycle(business_sizes))
        self.assertEqual(contract1.get_readable_business_size(),
                         'other than small business')
        self.assertEqual(
            contract2.get_readable_business_size(), 'small business')

    def test_get_education_code(self):
        c = get_contract_recipe().make()
        self.assertEqual(c.get_education_code('Bachelors'), 'BA')
        self.assertIsNone(c.get_education_code('Nursing'), None)

        with self.assertRaises(ValueError):
            c.get_education_code('Nursing', raise_exception=True)

    def test_normalize_rate(self):
        c = get_contract_recipe().make()
        self.assertEqual(c.normalize_rate('$1,000.00,'), 1000.0)

    def test_get_hourly_rate(self):
        c = self.make_contract_with_rates()
        self.assertEqual(c.get_hourly_rate(1), 100.00)
        self.assertEqual(c.get_hourly_rate(2), 102.20)
        self.assertEqual(c.get_hourly_rate(3), 103.30)
        self.assertEqual(c.get_hourly_rate(4), 104.40)
        self.assertEqual(c.get_hourly_rate(5), 105.50)

    def test_get_hourly_rate_raises_on_invalid_year(self):
        c = get_contract_recipe().make()
        with self.assertRaises(ValueError):
            c.get_hourly_rate(0)
        with self.assertRaises(ValueError):
            c.get_hourly_rate(6)

    def test_set_hourly_rate(self):
        c = get_contract_recipe().make()
        for i in range(1, 6):
            c.set_hourly_rate(i, 120)
            self.assertEqual(
                getattr(c, 'hourly_rate_year{}'.format(i)), 120)

    def test_set_hourly_rate_raises_on_invalid_year(self):
        c = get_contract_recipe().make()
        with self.assertRaises(ValueError):
            c.set_hourly_rate(0, 50)
        with self.assertRaises(ValueError):
            c.set_hourly_rate(6, 50)

    def test_escalate_hourly_rate_fields(self):
        c = get_contract_recipe().make()
        c.escalate_hourly_rate_fields(base_year_rate=100,
                                      escalation_rate=2.5)
        self.assertEqual(c.hourly_rate_year1, 100)
        self.assertAlmostEqual(c.hourly_rate_year2, Decimal(102.50), places=2)
        self.assertAlmostEqual(c.hourly_rate_year3, Decimal(105.06), places=2)
        self.assertAlmostEqual(c.hourly_rate_year4, Decimal(107.69), places=2)
        self.assertAlmostEqual(c.hourly_rate_year5, Decimal(110.38), places=2)

    def test_escalate_sets_prices_to_base_year_rate_when_no_escalation(self):
        c = get_contract_recipe().make()
        c.escalate_hourly_rate_fields(base_year_rate=125.40,
                                      escalation_rate=0)
        self.assertEqual(c.hourly_rate_year1, 125.40)
        self.assertEqual(c.hourly_rate_year2, 125.40)
        self.assertEqual(c.hourly_rate_year3, 125.40)
        self.assertEqual(c.hourly_rate_year4, 125.40)
        self.assertEqual(c.hourly_rate_year5, 125.40)

    def test_escalate_hourly_rate_fields_raises_on_invalid_rate(self):
        c = get_contract_recipe().make()
        with self.assertRaises(ValueError):
            c.escalate_hourly_rate_fields(base_year_rate=100,
                                          escalation_rate=-5)
        with self.assertRaises(ValueError):
            c.escalate_hourly_rate_fields(base_year_rate=100,
                                          escalation_rate=100)
        with self.assertRaises(ValueError):
            c.escalate_hourly_rate_fields(base_year_rate=100,
                                          escalation_rate=99.1)

    def test_update_price_fields(self):
        c = self.make_contract_with_rates(
            contract_start=datetime.date(2016, 2, 11),
            contract_end=datetime.date(2021, 2, 11))

        c.contract_year = 1
        c.update_price_fields()
        self.assertEqual(c.current_price, 100.00)
        self.assertEqual(c.next_year_price, 102.20)
        self.assertEqual(c.second_year_price, 103.30)

        c.contract_year = 2
        c.update_price_fields()
        self.assertEqual(c.current_price, 102.20)
        self.assertEqual(c.next_year_price, 103.30)
        self.assertEqual(c.second_year_price, 104.40)

        c.contract_year = 3
        c.update_price_fields()
        self.assertEqual(c.current_price, 103.30)
        self.assertEqual(c.next_year_price, 104.40)
        self.assertEqual(c.second_year_price, 105.50)

        c.contract_year = 4
        c.update_price_fields()
        self.assertEqual(c.current_price, 104.40)
        self.assertEqual(c.next_year_price, 105.50)
        self.assertIsNone(c.second_year_price)

        c.contract_year = 5
        c.update_price_fields()
        self.assertEqual(c.current_price, 105.50)
        self.assertIsNone(c.next_year_price)
        self.assertIsNone(c.second_year_price)

    def test_update_price_fields_works_for_future_contract_start(self):
        c = self.make_contract_with_rates(
            contract_start=datetime.date(2016, 2, 11),
            contract_end=datetime.date(2020, 2, 11))

        c.contract_year = 1
        c.update_price_fields()
        self.assertEqual(c.current_price, 100.00)
        self.assertEqual(c.next_year_price, 102.20)
        self.assertEqual(c.second_year_price, 103.30)

        c.contract_year = 0
        c.update_price_fields()
        self.assertEqual(c.current_price, None)
        self.assertEqual(c.next_year_price, 100.00)
        self.assertEqual(c.second_year_price, 102.20)

        c.contract_year = -1
        c.update_price_fields()
        self.assertEqual(c.current_price, None)
        self.assertEqual(c.next_year_price, None)
        self.assertEqual(c.second_year_price, 100.00)

        c.contract_year = -2
        c.update_price_fields()
        self.assertEqual(c.current_price, None)
        self.assertEqual(c.next_year_price, None)
        self.assertEqual(c.second_year_price, None)

    def test_update_price_fields_sets_to_None_when_current_year_gt_5(self):
        c = get_contract_recipe().make(
            contract_year=6,
            contract_start=datetime.date(2017, 2, 11),
            contract_end=datetime.date(2021, 2, 11))
        c.update_price_fields()
        self.assertIsNone(c.current_price)
        self.assertIsNone(c.next_year_price)
        self.assertIsNone(c.second_year_price)

    def test_update_price_fields_raises_when_no_contract_year(self):
        c = get_contract_recipe().make(contract_year=None)
        with self.assertRaises(ValueError):
            c.update_price_fields()

    def test_update_price_fields_takes_contract_end_into_account(self):
        c = self.make_contract_with_rates(
            contract_year=1,
            contract_start=datetime.date(2016, 2, 11),
            contract_end=datetime.date(2017, 1, 1))

        c.update_price_fields()
        self.assertEqual(c.current_price, 100.00)
        self.assertEqual(c.next_year_price, None)
        self.assertEqual(c.second_year_price, None)

        c.contract_end = datetime.date(2018, 1, 1)
        c.update_price_fields()
        self.assertEqual(c.current_price, 100.00)
        self.assertEqual(c.next_year_price, 102.20)
        self.assertEqual(c.second_year_price, None)

        c.contract_end = datetime.date(2019, 1, 1)
        c.update_price_fields()
        self.assertEqual(c.current_price, 100.00)
        self.assertEqual(c.next_year_price, 102.20)
        self.assertEqual(c.second_year_price, 103.30)

    def test_adjust_contract_year(self):
        c = get_contract_recipe().make(
            contract_start=datetime.date(2016, 2, 11))
        c.adjust_contract_year(
            current_date=datetime.date(2016, 2, 12))
        self.assertEqual(c.contract_year, 1)

        c.adjust_contract_year(
            current_date=datetime.date(2015, 2, 1))
        self.assertEqual(c.contract_year, 0)

    def test_adjust_contract_year_raises_when_no_contract_start(self):
        c = get_contract_recipe().make(contract_start=None)
        with self.assertRaises(ValueError):
            c.adjust_contract_year()

    def test_calculate_end_year(self):
        c = get_contract_recipe().make(
            contract_start=datetime.date(2016, 2, 11),
            contract_end=datetime.date(2020, 2, 12))
        self.assertEqual(c.calculate_end_year(), 5)

        c.contract_end = datetime.date(2018, 2, 12)
        self.assertEqual(c.calculate_end_year(), 3)

    def test_calculate_end_year_maxes_at_5(self):
        c = get_contract_recipe().make(
            contract_start=datetime.date(2016, 2, 11),
            contract_end=datetime.date(2030, 2, 12))
        self.assertEqual(c.calculate_end_year(), 5)

    def test_calculate_end_year_raises_when_no_contract_start_or_end(self):
        d = datetime.date(2016, 2, 11)
        c = get_contract_recipe().make(
            contract_start=None,
            contract_end=d)
        with self.assertRaises(ValueError):
            c.calculate_end_year()
        c.contract_start = d
        c.contract_end = None
        with self.assertRaises(ValueError):
            c.calculate_end_year()

    def test_calculate_end_year_raises_when_start_after_end(self):
        c = get_contract_recipe().make(
            contract_start=datetime.date(2020, 2, 11),
            contract_end=datetime.date(2015, 2, 12))
        with self.assertRaises(ValueError):
            c.calculate_end_year()


class BaseContractSearchTestCase(TestCase):
    CATEGORIES = []

    def assertCategoriesEqual(self, results, categories):
        result_categories = [r.labor_category for r in results]
        self.assertEqual(sorted(result_categories), sorted(categories))

    def setUp(self):
        self.contracts = get_contract_recipe().make(
            labor_category=cycle(self.CATEGORIES),
            _quantity=len(self.CATEGORIES)
        )


class ContractSearchTestCase(BaseContractSearchTestCase):
    CATEGORIES = [
        'Sign Language Interpretation',
        'Foreign Language Staff Interpreter (Spanish sign language)',
        'Aircraft Servicer',
        'Service Order Dispatcher',
        'Disposal Services',
        'Interpretation Services Class 4: Afrikan,Akan,Albanian',
        'Interpretation Services Class 1: Spanish',
        'Interpretation Services Class 2: French, German, Italian',
    ]

    def test_multi_phrase_search_works_with_single_word_phrase(self):
        results = Contract.objects.all().multi_phrase_search('interpretation')
        self.assertCategoriesEqual(results, [
            u'Sign Language Interpretation',
            u'Interpretation Services Class 4: Afrikan,Akan,Albanian',
            u'Interpretation Services Class 1: Spanish',
            u'Interpretation Services Class 2: French, German, Italian'
        ])

    def test_multi_phrase_search_works_with_multi_word_phrase(self):
        results = Contract.objects.all().multi_phrase_search(
            'interpretation services'
        )
        self.assertCategoriesEqual(results, [
            u'Interpretation Services Class 4: Afrikan,Akan,Albanian',
            u'Interpretation Services Class 1: Spanish',
            u'Interpretation Services Class 2: French, German, Italian'
        ])

    def test_multi_phrase_search_works_with_multiple_phrases(self):
        results = Contract.objects.all().multi_phrase_search(
            'interpretation services, disposal'
        )
        self.assertCategoriesEqual(results, [
            u'Disposal Services',
            u'Interpretation Services Class 4: Afrikan,Akan,Albanian',
            u'Interpretation Services Class 1: Spanish',
            u'Interpretation Services Class 2: French, German, Italian'
        ])

    def test_search_index_works_via_raw_sql(self):
        results = Contract.objects.raw(
            '''
            SELECT id, labor_category
            FROM contracts_contract
            WHERE search_index @@ to_tsquery('Interpretation')
            ORDER BY id
            '''
        )
        self.assertCategoriesEqual(results, [
            u'Sign Language Interpretation',
            u'Foreign Language Staff Interpreter (Spanish sign language)',
            u'Interpretation Services Class 4: Afrikan,Akan,Albanian',
            u'Interpretation Services Class 1: Spanish',
            u'Interpretation Services Class 2: French, German, Italian'
        ])


class UnicodeContractSearchTestCase(BaseContractSearchTestCase):
    CATEGORIES = [
        '\u5982',
        '\u679c',
    ]

    def test_search_finds_thing(self):
        results = Contract.objects.search('\u5982')
        self.assertCategoriesEqual(results, [
            '\u5982',
        ])


class NormalizedContractSearchTestCase(BaseContractSearchTestCase):
    CATEGORIES = [
        'Jr. Language Interpreter',
        'Junior Language Interpreter',
    ]

    def test_search_for_junior_finds_jr(self):
        results = Contract.objects.all().multi_phrase_search('junior')
        self.assertCategoriesEqual(results, [
            'Jr. Language Interpreter',
            'Junior Language Interpreter',
        ])

    def test_search_for_jr_finds_junior(self):
        results = Contract.objects.all().multi_phrase_search('jr')
        self.assertCategoriesEqual(results, [
            'Jr. Language Interpreter',
            'Junior Language Interpreter',
        ])


class SearchIndexTests(TestCase):
    GET_SCHEMA_SQL = """
    SELECT column_name, data_type, column_default, is_nullable
      FROM information_schema.columns
      WHERE table_name = 'contracts_contract'
        AND column_name = 'search_index'
    """

    def test_schema_is_what_we_expect(self):
        with connection.cursor() as cursor:
            cursor.execute(self.GET_SCHEMA_SQL)
            row = cursor.fetchone()
            self.assertEqual(row, (
                'search_index',
                'tsvector',
                None,
                'NO',
            ))
