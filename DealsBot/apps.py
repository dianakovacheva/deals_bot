from django.apps import AppConfig


class DealsbotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'DealsBot'

    def ready(self):
        import deals_bot.celery