from django.apps import AppConfig


class DefaultContractsApp(AppConfig):
    name = 'contracts'
    verbose_name = 'Contracts'

    def ready(self):
        from . import signals  # noqa
