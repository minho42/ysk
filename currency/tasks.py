from celery import Celery
from celery.schedules import crontab

from ysk.celery import app

from .views import get_new_api_data


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(minute="*/5"), fetch_all.s(), name="")


@app.task
def fetch_all():
    get_new_api_data()
