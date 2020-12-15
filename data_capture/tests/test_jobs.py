from unittest.mock import patch
from django.core import mail
from django.test import TestCase
from rq import SimpleWorker
import django_rq

from .common import create_bulk_upload_contract_source
from .. import jobs


def process_worker_jobs():
    # We need to do this while testing to avoid strange errors on Circle.
    #
    # See:
    #
    #   http://python-rq.org/docs/testing/
    #   https://github.com/ui/django-rq/issues/123

    queue = django_rq.get_queue()
    worker = SimpleWorker([queue], connection=queue.connection)
    worker.work(burst=True)


class ProcessBulkUploadTests(TestCase):
    @patch.object(jobs, '_process_bulk_upload')
    def test_sends_email_on_failure(self, mock):
        mock.side_effect = Exception('KABLOOEY')
        src = create_bulk_upload_contract_source(user='foo@example.org')
        src.save()
        jobs.process_bulk_upload_and_send_email(src.id)
        self.assertEqual(len(mail.outbox), 1)

        message = mail.outbox[0]
        self.assertEqual(message.recipients(), ['foo@example.org'])
        self.assertRegexpMatches(message.body, 'KABLOOEY')

    def test_sends_email_on_success(self):
        src = create_bulk_upload_contract_source(user='foo@example.org')
        src.save()
        jobs.process_bulk_upload_and_send_email(src.id)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), ['foo@example.org'])

    def test_contract_creation_batching_yields_leftovers(self):
        rows = [['']] * 3
        generator = jobs._create_contract_batches(
            None,
            batch_size=2,
            rows=rows
        )

        contracts, bad_rows = next(generator)
        self.assertEqual(contracts, [])
        self.assertEqual(len(bad_rows), 2)

        contracts, bad_rows = next(generator)
        self.assertEqual(contracts, [])
        self.assertEqual(len(bad_rows), 1)

        with self.assertRaises(StopIteration):
            next(generator)

    def test_contract_creation_batching_does_not_yield_empty_leftovers(self):
        rows = [['']] * 2
        generator = jobs._create_contract_batches(
            None,
            batch_size=2,
            rows=rows
        )

        contracts, bad_rows = next(generator)
        self.assertEqual(contracts, [])
        self.assertEqual(len(bad_rows), 2)

        with self.assertRaises(StopIteration):
            next(generator)
