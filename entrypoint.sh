#!/bin/sh
python manage.py migrate
python manage.py collectstatic --no-input
gunicorn cms.wsgi:application -c gunicorn.conf.py
