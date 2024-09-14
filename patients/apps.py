from django.apps import AppConfig


class PatientsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'patients'


# WHAT MAKES THE SIGNALS WORKS - auto create profile
    def ready(self):
        import patients.signals
