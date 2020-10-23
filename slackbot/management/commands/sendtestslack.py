import djclick as click
from django.conf import settings
from django.core.management.base import CommandError

from slackbot.bot import sendmsg
from calc.site_utils import absolutify_url


@click.command()
def command() -> None:
    url = absolutify_url('/')

    if not settings.SLACKBOT_WEBHOOK_URL:
        raise CommandError("SLACKBOT_WEBHOOK_URL must be configured.")

    if not sendmsg(f"Hi, this is a test message from <{url}|CALC>!"):
        raise CommandError("Sending test Slack message failed.")

    print("Test Slack message sent successfully!")
