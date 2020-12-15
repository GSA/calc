# This file is based on the following from Django 1.9:
# https://github.com/django/django/blob/master/django/core/management/commands/sendtestemail.py

import socket
from django.core.management.base import BaseCommand
from django.utils import timezone

from calc.site_utils import absolutify_url
from data_capture import email


class Command(BaseCommand):
    help = "Sends a test HTML email to the email addresses specified as arguments."  # NOQA
    missing_args_message = "You must specify some email recipients."  # NOQA

    def add_arguments(self, parser):
        parser.add_argument(
            'email', nargs='*',
            help='One or more email addresses to send a test email to.',
        )

    def handle(self, *args, **kwargs):
        subject = 'Test HTML email from %s on %s' % (socket.gethostname(), timezone.now())  # NOQA

        email.send_mail(
            subject=subject,
            to=kwargs['email'],
            template='email/test_email.html',
            ctx={
                'site_url': absolutify_url('/')
            },
        )
