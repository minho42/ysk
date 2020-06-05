release: python manage.py migrate
web: daphne ysk.asgi:application --port $PORT --bind 0.0.0.0 -v2
celeryworker: celery -A ysk worker --beat --scheduler django --loglevel=info
