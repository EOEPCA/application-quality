from django.apps import AppConfig


class BackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend'

    def ready(self):
        import backend.tasks  # noqa: F401  # pylint: disable=C0415, W0611
