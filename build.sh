#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt


echo "--- DEBUG: Current Directory ---"
pwd
ls -la

echo "--- DEBUG: Static Directory Content ---"
ls -R static || echo "Static directory not found"

python manage.py collectstatic --no-input -v 2
python manage.py migrate
