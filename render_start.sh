#!/usr/bin/env bash
set -o errexit

# Apply database migrations
python manage.py migrate

# Create superuser if configured
python manage.py ensure_admin

# Start Gunicorn
gunicorn config.wsgi:application
