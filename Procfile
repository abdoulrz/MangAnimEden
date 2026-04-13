web: gunicorn config.wsgi:application --workers 3 --threads 2 --timeout 120
worker: celery -A config worker -l info
