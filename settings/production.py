from .base import *

DEBUG = False

ALLOWED_HOSTS += [
    "audkrw.com",
    "www.audkrw.com",
]

REDIS_URL = env("REDIS_URL")

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
