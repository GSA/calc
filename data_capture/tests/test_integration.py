import io
import django.contrib.auth
from django.conf.urls import url
from django.test import override_settings
from django.http import HttpResponse
from django.core.management import call_command

from calc.urls import urlpatterns
from calc.tests.common import BaseLoginTestCase
from data_capture.tests.common import FAKE_SCHEDULE, FAKE_SCHEDULE_EXAMPLE_PATH
from data_capture.models import SubmittedPriceList
from .browsers import BrowserTestCase


USERNAME = 'boop'
PASSWORD = 'passwordy'


def autologin(request):
    user = django.contrib.auth.authenticate(
        username=USERNAME,
        password=PASSWORD
    )
    if user is None:
        raise Exception('Unable to authenticate')
    django.contrib.auth.login(request, user)

    # We used to enable safe mode to reduce the chance of JS race conditions
    # getting in the way, but its overlay sometimes gets in the way of
    # clicking on elements, so we're just disabling it for now.
    #
    # from frontend import safe_mode
    # request.session[safe_mode.SESSION_KEY] = True

    return HttpResponse('{} is now logged in'.format(
        user.email
    ))


urlpatterns += [
    url(r'^autologin/$', autologin),
]


@override_settings(
    ROOT_URLCONF=__name__,
    DATA_CAPTURE_SCHEDULES=[FAKE_SCHEDULE],
    # This will make tests run faster.
    PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'],
    # Ignore our custom auth backend so we can log the user in via
    # Django 1.8's login helpers.
    AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'],
)
class DataCaptureTests(BrowserTestCase):
    def get_step_title(self):
        return self.get_title().split(' / ')[-1]

    def test_data_capture(self):
        call_command('initgroups', stdout=io.StringIO())
        t = BaseLoginTestCase()
        user = t.create_user(
            username=USERNAME,
            password=PASSWORD,
            email='boop.jones@gsa.gov',
            groups=('Contract Officers',)
        )
        self.load('/autologin')
        self.load('/data-capture/step/1')

        # This first form has no ID, and that appears to be OK
        form = self.get_form('form')
        form.set_text('contract_number', 'GS-123-4567')
        form.submit()

        self.assertEqual(
            self.get_step_title(),
            'Step 2 of 5: Enter vendor details'
        )

        form = self.get_form('#vendor-contract-form')
        form.set_text('vendor_name', 'Battaglia Sausage Peddlers, Inc.')
        form.set_radio('is_small_business', 0)
        form.set_radio('contractor_site', 2)
        form.set_date('contract_start', 4, 28, 2016)
        form.set_date('contract_end', 3, 27, 2017)
        form.submit()

        self.assertEqual(
            self.get_step_title(),
            'Step 3 of 5: Upload price list'
        )

        form = self.get_form('form')
        form.set_file('file', FAKE_SCHEDULE_EXAMPLE_PATH)
        form.submit()

        self.assertEqual(
            self.get_step_title(),
            'Step 4 of 5: Verify data'
        )

        self.get_form('form').submit()

        self.assertEqual(
            self.get_step_title(),
            'Step 5 of 5: Data submitted for review!'
        )

        p = SubmittedPriceList.objects.all()[0]
        self.assertEqual(p.contract_number, 'GS-123-4567')
        self.assertEqual(p.vendor_name, 'Battaglia Sausage Peddlers, Inc.')
        self.assertEqual(p.is_small_business, True)
        self.assertEqual(p.contractor_site, 'Both')
        self.assertEqual(p.contract_start.year, 2016)
        self.assertEqual(p.contract_start.month, 4)
        self.assertEqual(p.contract_start.day, 28)
        self.assertEqual(p.contract_end.year, 2017)
        self.assertEqual(p.contract_end.month, 3)
        self.assertEqual(p.contract_end.day, 27)
        self.assertEqual(p.escalation_rate, 0)
        self.assertEqual(p.submitter, user)
        self.assertEqual(p.schedule, FAKE_SCHEDULE)

        r = p.rows.all()[0]
        self.assertEqual(r.labor_category, 'Project Manager')
