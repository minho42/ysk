from .base import *

DEBUG = False

ALLOWED_HOSTS += [
    "audkrw.com",
    "www.audkrw.com",
    "149.28.174.146",
]

REDIS_URL = get_env_variable("REDIS_URL")

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
