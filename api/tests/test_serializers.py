from django.test import SimpleTestCase, TestCase
from rest_framework.serializers import ValidationError

from contracts.models import Contract
from api.serializers import EducationLevelField, ContractSerializer


class EducationLevelFieldTests(SimpleTestCase):
    def test_returns_edu_code(self):
        self.assertEqual(
            EducationLevelField().to_internal_value('Bachelors'),
            'BA'
        )

    def test_raises_validation_error(self):
        f = EducationLevelField()
        msg = 'Invalid education level: lol'
        with self.assertRaisesRegex(ValidationError, msg):
            f.to_internal_value('lol')


class ContractListSerializerTests(TestCase):
    def test_search_index_is_updated(self):
        rates = [{
            'idv_piid': 'GS-123-4567',
            'vendor_name': 'Blarg Inc.',
            'labor_category': 'Software Engineer',
            'education_level': 'Bachelors',
            'min_years_experience': 2,
            'current_price': 100,
            'hourly_rate_year1': 100
        }]
        serializer = ContractSerializer(data=rates, many=True)
        if not serializer.is_valid():
            raise AssertionError(serializer.errors)
        serializer.save()
        results = Contract.objects.all().multi_phrase_search('engineer').all()
        self.assertEqual([r.labor_category for r in results], ['Software Engineer'])
