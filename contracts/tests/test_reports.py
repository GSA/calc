from django.test import TestCase
from django.core.management import call_command

from contracts import reports
# from contracts.loaders.region_10 import FEDERAL_MIN_CONTRACT_RATE
from contracts.mommy_recipes import get_contract_recipe


class Tests(TestCase):
    def test_data_quality_report_command_does_not_explode(self):
        get_contract_recipe().make(_quantity=50)
        call_command('data_quality_report')

    def test_data_quality_report_view_does_not_explode(self):
        get_contract_recipe().make(_quantity=50)
        res = self.client.get('/data-quality-report/')
        self.assertEqual(res.status_code, 200)

    # def test_outliers_works(self):
    #     get_contract_recipe().make(
    #         labor_category='senior outlier',
    #         min_years_experience=1,
    #         education_level='HS',
    #         current_price=999999
    #     )
    #     get_contract_recipe().make(
    #         labor_category='not an outlier',
    #         min_years_experience=1,
    #         education_level='HS',
    #         current_price=FEDERAL_MIN_CONTRACT_RATE
    #     )

    #     self.assertEqual(reports.outliers.Metric().count(), 1)

    #     res = self.client.get('/data-quality-report/outliers/')
    #     self.assertContains(res, 'senior outlier')
    #     self.assertNotContains(res, 'not an outlier')

    def test_dupes_works(self):
        get_contract_recipe().make(labor_category='not a dupe')

        res = self.client.get('/data-quality-report/dupes/')
        self.assertNotContains(res, 'Examples')
        self.assertEqual(reports.dupes.Metric().count(), 0)

        for level in ['junior', 'senior', 'executive']:
            for sin in ['874-1', '874-2', '874-3', '874-4']:
                get_contract_recipe().make(
                    vendor_name='foo',
                    labor_category=f'{level} dupe',
                    idv_piid='GS-123-4567',
                    current_price=50,
                    sin=sin
                )

        self.assertEqual(reports.dupes.Metric().count(), 12)

        res = self.client.get('/data-quality-report/dupes/')
        self.assertContains(res, 'Examples')
        self.assertContains(res, 'senior dupe')
        self.assertNotContains(res, 'not a dupe')

    def test_invalid_data_quality_report_detail_returns_404(self):
        res = self.client.get('/data-quality-report/boooooooop/')
        self.assertEqual(res.status_code, 404)
