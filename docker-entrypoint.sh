#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- Starting Database Migrations ---"
python manage.py migrate --noinput
python manage.py init_prod

echo "--- Starting Application Server ---"
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0
