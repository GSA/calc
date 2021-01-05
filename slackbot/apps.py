from django.apps import AppConfig


class SlackbotConfig(AppConfig):
    name = 'slackbot'

    def ready(self):
        from . import signals  # NOQA
