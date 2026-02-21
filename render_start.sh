#!/usr/bin/env bash
set -o errexit

# Apply database migrations
python manage.py migrate

# Sync Site domain with Render hostname (critical for Google Auth)
python fix_site_domain.py

# Create superuser if configured
python manage.py ensure_admin

# Start Gunicorn
gunicorn config.wsgi:application
