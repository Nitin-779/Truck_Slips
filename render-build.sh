#!/usr/bin/env bash
# exit on error
set -o errexit  

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate

# Create superuser (only if it doesn’t exist)
python manage.py createsuperuser --noinput || true
