from django.apps import AppConfig


class CseFestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cse_fest'

    def ready(self):
        import cse_fest.signals  # noqa
