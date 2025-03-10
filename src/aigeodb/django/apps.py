from django.apps import AppConfig


class AigeodbConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "aigeodb.django"
    verbose_name = "AigeoDB"

    def ready(self):
        """Perform initialization when Django starts."""
        pass
