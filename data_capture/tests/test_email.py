from datetime import datetime

from django.core import mail
from django.core.urlresolvers import reverse
from django.test import override_settings
from django.contrib.auth.models import User
from freezegun import freeze_time

from .. import email
from ..models import SubmittedPriceList
from .common import create_bulk_upload_contract_source, FAKE_SCHEDULE
from .test_models import ModelTestCase


@freeze_time(datetime(2017, 1, 8, 20, 51, 0))
@override_settings(DATA_CAPTURE_SCHEDULES=[FAKE_SCHEDULE],

                   # This ensures absolute URLs produced by our code
                   # are https-based.
                   SECURE_SSL_REDIRECT=True,

                   DEFAULT_FROM_EMAIL='hi@hi.com',
                   HELP_EMAIL="help@help.com",)
class EmailTests(ModelTestCase):
    '''Tests for email sending functions'''

    def assertHasOneHtmlAlternative(self, message):
        content_types = [alt[1] for alt in message.alternatives]
        self.assertIn('text/html', content_types)
        self.assertEqual(len(content_types), 1)

    def assertHasLink(self, message, url):
        html_content = [content for (content, content_type)
                        in message.alternatives
                        if content_type == 'text/html'][0]
        self.assertIn(url, html_content)

    def assertHasDetailsLink(self, price_list, message):
        details_link = 'https://example.com' + reverse(
            'data_capture:price_list_details', kwargs={'id': price_list.pk})

        self.assertHasOneHtmlAlternative(message)
        self.assertHasLink(message, details_link)

    def assertHasReplyTo(self, message, reply_to_email='help@help.com'):
        self.assertEqual(len(message.reply_to), 1)
        self.assertEqual(message.reply_to[0], reply_to_email)

    def test_send_mail_works(self):
        result = email.send_mail(
            subject='test email',
            template='data_capture/tests/test_email.html',
            ctx={},
            to=['test@test.com'],
            reply_to=['reply-test@test.com'],
        )
        self.assertEqual(result, 1)
        message = mail.outbox[0]
        self.assertHasReplyTo(message, 'reply-test@test.com')
        self.assertEqual(message.recipients(), ['test@test.com'])
        self.assertEqual(message.subject, 'test email')
        self.assertEqual(message.from_email, 'hi@hi.com')
        self.assertEqual(message.body, 'test body')
        self.assertHasOneHtmlAlternative(message)
        self.assertEqual(message.alternatives[0][0], '<p>test body</p>')

    def test_price_list_approved(self):
        price_list = self.create_price_list(
            status=SubmittedPriceList.STATUS_APPROVED)
        price_list.save()
        result = email.price_list_approved(price_list)
        self.assertTrue(result.was_successful)
        message = mail.outbox[0]
        self.assertEqual(message.recipients(), [self.user.email])
        self.assertEqual(message.subject, 'CALC Price List Approved')
        self.assertEqual(message.from_email, 'hi@hi.com')
        self.assertIn('Jan. 8, 2017 at 3:51 p.m. (EST)', message.body)
        self.assertHasOneHtmlAlternative(message)
        self.assertHasDetailsLink(price_list, message)
        self.assertHasReplyTo(message)
        self.assertEqual(result.context['price_list'], price_list)

    def test_price_list_approved_raises_if_not_approved(self):
        price_list = self.create_price_list(
            status=SubmittedPriceList.STATUS_UNREVIEWED)
        price_list.save()
        with self.assertRaises(AssertionError):
            email.price_list_approved(price_list)

    def test_price_list_retired(self):
        price_list = self.create_price_list(
            status=SubmittedPriceList.STATUS_RETIRED)
        price_list.save()
        result = email.price_list_retired(price_list)
        self.assertTrue(result.was_successful)
        message = mail.outbox[0]
        self.assertEqual(message.recipients(), [self.user.email])
        self.assertEqual(message.subject, 'CALC Price List Retired')
        self.assertEqual(message.from_email, 'hi@hi.com')
        self.assertIn('Jan. 8, 2017 at 3:51 p.m. (EST)', message.body)
        self.assertHasOneHtmlAlternative(message)
        self.assertHasDetailsLink(price_list, message)
        self.assertHasReplyTo(message)
        self.assertEqual(result.context['price_list'], price_list)

    def test_price_list_retired_raises_if_approved(self):
        price_list = self.create_price_list(
            status=SubmittedPriceList.STATUS_APPROVED)
        price_list.save()
        with self.assertRaises(AssertionError):
            email.price_list_retired(price_list)

    def test_price_list_rejected(self):
        price_list = self.create_price_list(
            status=SubmittedPriceList.STATUS_REJECTED)
        price_list.save()
        result = email.price_list_rejected(price_list)
        self.assertTrue(result.was_successful)
        message = mail.outbox[0]
        self.assertEqual(message.recipients(), [self.user.email])
        self.assertEqual(message.subject, 'CALC Price List Rejected')
        self.assertEqual(message.from_email, 'hi@hi.com')
        self.assertIn('Jan. 8, 2017 at 3:51 p.m. (EST)', message.body)
        self.assertHasOneHtmlAlternative(message)
        self.assertHasDetailsLink(price_list, message)
        self.assertHasReplyTo(message)
        self.assertEqual(result.context['price_list'], price_list)

    def test_price_list_rejected_raises_if_wrong_status(self):
        price_list = self.create_price_list(
            status=SubmittedPriceList.STATUS_APPROVED)
        price_list.save()
        with self.assertRaises(AssertionError):
            email.price_list_rejected(price_list)

    def test_bulk_uploaded_succeeded(self):
        src = create_bulk_upload_contract_source(
            self.user)
        src.save()
        result = email.bulk_upload_succeeded(src, 5, 2)
        self.assertTrue(result.was_successful)
        message = mail.outbox[0]
        self.assertEqual(message.recipients(), [self.user.email])
        self.assertEqual(
            message.subject,
            'CALC Region 10 bulk data results - upload #{}'.format(src.pk))
        self.assertEqual(message.from_email, 'hi@hi.com')
        self.assertIn('Jan. 8, 2017 at 3:51 p.m. (EST)', message.body)
        self.assertHasOneHtmlAlternative(message)
        self.assertHasReplyTo(message)
        self.assertIn('r10_upload_link', result.context)
        self.assertEqual(result.context['num_contracts'], 5)
        self.assertEqual(result.context['num_bad_rows'], 2)

    def test_bulk_upload_failed(self):
        src = create_bulk_upload_contract_source(
            self.user)
        src.save()
        result = email.bulk_upload_failed(src, 'traceback_contents')
        self.assertTrue(result.was_successful)
        message = mail.outbox[0]
        self.assertEqual(message.recipients(), [self.user.email])
        self.assertEqual(
            message.subject,
            'CALC Region 10 bulk data results - upload #{}'.format(src.pk))
        self.assertEqual(message.from_email, 'hi@hi.com')
        self.assertIn('Jan. 8, 2017 at 3:51 p.m. (EST)', message.body)
        self.assertHasOneHtmlAlternative(message)
        self.assertHasReplyTo(message)
        self.assertEqual(result.context['traceback'], 'traceback_contents')
        self.assertIn('r10_upload_link', result.context)
        self.assertHasLink(
            message,
            'https://example.com/data-capture/bulk/region-10/step/1')

    def test_approval_reminder(self):
        User.objects.create_superuser('admin', 'admin@localhost', 'password')
        User.objects.create_superuser('admin2', 'admin2@localhost', 'password')
        User.objects.create_superuser('blankadmin', '', 'password')
        count = 5
        result = email.approval_reminder(count)
        self.assertTrue(result.was_successful)
        message = mail.outbox[0]
        self.assertEqual(message.recipients(),
                         ['admin@localhost', 'admin2@localhost'])
        self.assertEqual(
            message.subject,
            'CALC Reminder - {} price lists not reviewed'.format(count)
        )
        self.assertEqual(message.from_email, 'hi@hi.com')
        self.assertHasOneHtmlAlternative(message)
        self.assertHasReplyTo(message)
        self.assertHasLink(
            message,
            'https://example.com/admin/data_capture/unreviewedpricelist/')
