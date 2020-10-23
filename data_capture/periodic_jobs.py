import logging

from . import email
from .models import SubmittedPriceList

logger = logging.getLogger('rq_scheduler')


def send_admin_approval_reminder_email(threshold=10):
    logger.info('Processing periodic reminder about unreviewed Price Lists')

    count_unreviewed = SubmittedPriceList.objects.filter(
        status=SubmittedPriceList.STATUS_UNREVIEWED).count()

    if count_unreviewed >= threshold:
        logger.info(' -- Number unreviewed is greater than {}, '
                    'sending reminder email'.format(threshold))
        email.approval_reminder(count_unreviewed)
    else:
        logger.info(' -- Number unreviewed is less than {}, no email '
                    'will be sent'.format(threshold))
