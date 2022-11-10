from django.apps import AppConfig


class SpiderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'spider'

    def ready(self):
        """ Added app scheduler for Spider """
        from artradio_schedulers.spider import run_spider_scheduler
        from .views import handler_spider_radio, logger
        logger.debug("Starting scheduler for Spider")
        run_spider_scheduler(handler_spider_radio)
