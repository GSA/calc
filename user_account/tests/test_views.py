from model_mommy import mommy

from calc.tests.common import ProtectedViewTestCase
from data_capture.models import SubmittedPriceList


class AccountTests(ProtectedViewTestCase):
    url = '/account/'

    def test_get_is_ok(self):
        self.login()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_has_context_vars(self):
        self.login()
        res = self.client.get(self.url)
        ctx = res.context
        self.assertIn('total_approved', ctx)
        self.assertIn('total_unreviewed', ctx)
        self.assertIn('total_rejected', ctx)
        self.assertIn('total_submitted', ctx)
        self.assertIn('recently_approved_price_lists', ctx)
        self.assertIn('recently_submitted_price_lists', ctx)

    def test_context_var_values_are_correct(self):
        user = self.login()
        mommy.make(SubmittedPriceList,
                   submitter=user,
                   status=SubmittedPriceList.STATUS_UNREVIEWED,
                   _quantity=6)

        mommy.make(SubmittedPriceList,
                   submitter=user,
                   status=SubmittedPriceList.STATUS_APPROVED,
                   _quantity=6)

        mommy.make(SubmittedPriceList,
                   submitter=user,
                   status=SubmittedPriceList.STATUS_REJECTED,
                   _quantity=1)

        res = self.client.get(self.url)
        ctx = res.context
        self.assertEqual(ctx['total_approved'], 6)
        self.assertEqual(ctx['total_unreviewed'], 6)
        self.assertEqual(ctx['total_rejected'], 1)
        self.assertEqual(ctx['total_submitted'], 13)

        # The view should only show the 5 most recent price lists
        self.assertEqual(len(ctx['recently_submitted_price_lists']), 5)
        self.assertEqual(len(ctx['recently_approved_price_lists']), 5)
