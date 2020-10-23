import logging
from django.apps import AppConfig

import django_rq


class DefaultDataCaptureApp(AppConfig):
    '''
    Default Data Capture app
    '''

    name = 'data_capture'
    verbose_name = 'User-submitted CALC data'

    def ready(self):
        from . import signals  # noqa


class DataCaptureSchedulerApp(AppConfig):
    '''
    Special DataCapture app for use as a singleton that launches periodic
    scheduled jobs.
    This app should only be used by the scheduler process.
    '''

    name = 'data_capture'
    verbose_name = 'CALC Data Capture RQ Scheduler'

    # every Monday at noon, but scheduler uses UTC so it will be 5AM Pacific
    admin_reminder_cron = '* 12 * * MON'
    rq_queue_name = 'default'

    @classmethod
    def get_scheduler(cls):
        return django_rq.get_scheduler(cls.rq_queue_name)

    def ready(self):
        # Import needs to happen after app is ready
        from . import periodic_jobs

        logger = logging.getLogger('rq_scheduler')

        scheduler = self.get_scheduler()

        # Cancel any jobs already in the scheduler. Jobs can be left dangling
        # from any restart of this custom AppConfig.
        for job in scheduler.get_jobs():
            scheduler.cancel(job)

        # Add cron-type job to send a reminder email to the CALC admins
        # about approving price lists
        logger.info('Adding send_admin_approval_reminder_email job on cron '
                    'schedule "{}"'.format(self.admin_reminder_cron))
        scheduler.cron(self.admin_reminder_cron,
                       periodic_jobs.send_admin_approval_reminder_email)
