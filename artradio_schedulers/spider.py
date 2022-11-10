from typing import Callable

from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from rest_framework.response import Response


def spider_scheduler() -> CronTrigger:
    sched_conf = settings.YAML_CONFIG_MAP.get("Spider Scheduler")
    if not sched_conf:
        raise FileNotFoundError("Yaml config file not found")
    return CronTrigger(**sched_conf.get("Cron"))


def run_spider_scheduler(callable_job: Callable[[dict], Response]) -> None:
    trigger = spider_scheduler()
    scheduler = BackgroundScheduler()
    scheduler.add_job(callable_job, trigger=trigger)
    scheduler.start()


