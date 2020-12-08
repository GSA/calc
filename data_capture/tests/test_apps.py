from django.test import TestCase, override_settings
from django.apps import apps

import django_rq

from .. import periodic_jobs
from ..apps import DataCaptureSchedulerApp


@override_settings(INSTALLED_APPS=[
    'data_capture.apps.DataCaptureSchedulerApp'
])
class DataCaptureSchedulerAppTests(TestCase):

    def test_data_capture_scheduler_app_adds_cron_job(self):
        config = apps.get_app_config('data_capture')
        self.assertIsInstance(config, DataCaptureSchedulerApp)
        config.ready()  # call the ready() method
        scheduler = django_rq.get_scheduler('default')
        jobs = scheduler.get_jobs()
        job_list = list(jobs)
        self.assertEqual(len(job_list), 1)
        the_job = job_list[0]
        self.assertEqual(
            the_job.func,
            periodic_jobs.send_admin_approval_reminder_email)
        self.assertEqual(the_job.meta['cron_string'], "* 12 * * MON")
