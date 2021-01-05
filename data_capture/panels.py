from debug_toolbar.panels import Panel

from .apps import DataCaptureSchedulerApp


class ScheduledJobsPanel(Panel):
    '''
    A Django Debug Toolbar panel that displays information about
    scheduled jobs.
    '''

    title = 'Scheduled Jobs'

    template = 'data_capture/panels/jobs.html'

    def generate_stats(self, request, response):
        scheduler = DataCaptureSchedulerApp.get_scheduler()

        self.record_stats({
            'scheduled_jobs': scheduler.get_jobs(with_times=True)
        })
