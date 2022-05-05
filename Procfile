release: python manage.py migrate
web: gunicorn ysk.wsgi
celeryworker: celery -A ysk worker --beat --scheduler django --loglevel=info
