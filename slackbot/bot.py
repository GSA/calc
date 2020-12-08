import json
import requests
import logging
from typing import Dict
from django.conf import settings
# from django.contrib.sites.models import Site
# from django.contrib.staticfiles.storage import staticfiles_storage

# from calc.site_utils import absolutify_url


# Timeout, in seconds, after we give up on Slack. Since Slack isn't
# mission-critical and we want to keep the site responsive to end-users,
# this can be pretty low.
TIMEOUT = 3


logger = logging.getLogger('slackbot')


def post_to_webhook(payload: Dict[str, str]):
    res = requests.post(
        settings.SLACKBOT_WEBHOOK_URL,
        data={'payload': json.dumps(payload)},
        timeout=TIMEOUT)
    res.raise_for_status()


def sendmsg(text: str) -> bool:
    '''
    Sends a message to Slack with the given text, formatted in the
    style described at https://api.slack.com/incoming-webhooks.

    This function will log any exceptions that occur due to network
    errors, and will not re-raise them. Thus it can safely be
    used without having to worry about taking down the whole app if
    Slack happens to be down.

    Returns True if the message was successfully sent, False otherwise.
    '''

    # payload = {
    #     'text': text,
    #     'username': Site.objects.get_current().name,
    #     'icon_url': absolutify_url(staticfiles_storage.url(
    #         'frontend/images/price-callout/mule.png')),
    # }
    # if settings.SLACKBOT_WEBHOOK_URL:
    #     try:
    #         post_to_webhook(payload)
    #         return True
    #     except Exception:
    #         logger.exception('Error occurred when sending Slack message.')
    # else:
    #     logger.debug('SLACKBOT_WEBHOOK_URL is empty; not sending message.')

    return False
