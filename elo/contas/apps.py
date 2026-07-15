from django.apps import AppConfig


class ContasConfig(AppConfig):
    name = 'contas'

    def ready(self):
        from . import signals  # noqa: F401  registra os sinais
