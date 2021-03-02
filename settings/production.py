from .base import *

DEBUG = False

ALLOWED_HOSTS += [
    "audkrw.com",
    "www.audkrw.com",
]

REDIS_URL = env("REDIS_URL")

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL


# Sentry
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration

sentry_sdk.init(
    dsn="https://0ef35c90768b486e89b1e52933eff293@o410328.ingest.sentry.io/5656262",
    integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration()],
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
)

