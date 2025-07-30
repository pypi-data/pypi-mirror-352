from django.apps import AppConfig


class MoniAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'moni_auth'

    def ready(self):
        from moni_auth import signals  # NOQA
