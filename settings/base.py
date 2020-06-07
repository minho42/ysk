import django_heroku
import os

from django.core.exceptions import ImproperlyConfigured


def get_env_variable(var_name):
    """Get the environment variable or return exception."""
    try:
        return os.environ.get(var_name)
    except KeyError:
        error_msg = f"Set the {var_name} environment variable"
        raise ImproperlyConfigured(error_msg)


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

SECRET_KEY = get_env_variable("CURRENCY_SECRET_KEY")

DEBUG = False

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "ysk.herokuapp.com",
    "audkrw.com",
]
# <-- added for bebug_toolbar to appear
INTERNAL_IPS = ["localhost", "127.0.0.1"]

INSTALLED_APPS = [
    "django.contrib.sites",
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # third party apps
    "rest_framework",
    "rest_framework.authtoken",
    "django_celery_beat",
    # local apps
    "currency",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # The WhiteNoise middleware should be placed directly after the Django SecurityMiddleware and before all other middleware
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ysk.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # `allauth` needs this from django
                "django.template.context_processors.request",
                # this allows navbar.html to access {{ MEDIA_URL }}
                "django.template.context_processors.media",
            ]
        },
    }
]

AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)

CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = (
    # TODO Set this property for production
    "http://localhost:3000",
    "https://127.0.0.1:8080",
    "https://127.0.0.1:8000",
)

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAdminUser"],
    # "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # "rest_framework_simplejwt.authentication.JWTAuthentication",
        # "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
}

SITE_ID = 1

WSGI_APPLICATION = "ysk.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "currency",
        "USER": "currencyuser",
        "PASSWORD": get_env_variable("CURRENCY_DB_PASSWORD"),
        "HOST": "localhost",
        "PORT": "5432",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ??change format to en_AU
# https://github.com/django/django/blob/master/django/conf/locale/en_AU/formats.py
# from django.conf.locale.en import formats as en_formats
# en_formats.DATETIME_FORMAT =
LANGUAGE_CODE = "en-us"

# https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
TIME_ZONE = "Australia/Sydney"

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
# http://whitenoise.evans.io/en/stable/django.html
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# Sending gmail
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "minho42@gmail.com"
EMAIL_HOST_PASSWORD = get_env_variable("GOOGLE_PASSWORD")
EMAIL_PORT = "587"
EMAIL_USE_TLS = True

# CELERY STUFF
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
# CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = "Australia/ACT"
CELERY_TASK_SOFT_TIME_LIMIT = 120


# Security
X_FRAME_OPTIONS = "DENY"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_SSL_REDIRECT = True
# CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
# SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True


django_heroku.settings(locals())
