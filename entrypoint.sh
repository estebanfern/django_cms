#!/bin/sh

# Ejecutar las migraciones solo si se especifica
if [ "$RUN_MIGRATIONS" = "true" ]; then
    python manage.py migrate
fi

# Ejecutar collectstatic solo si se especifica
if [ "$RUN_COLLECTSTATIC" = "true" ]; then
    python manage.py collectstatic --no-input
fi

# Crear las tareas programadas
python manage.py crontab add

gunicorn cms.wsgi:application -c gunicorn.conf.py
