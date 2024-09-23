#!/bin/sh

if [ "$1" = "workers" ]; then
    # shift  # Remover "celery" del argumento
    # celery "$@"  # Ejecutar el comando de celery con los argumentos restantes
    celery -A cms worker -f /app/logs/workers.log
elif [ "$1" = "scheduled" ]; then
    celery -A cms beat -f /app/logs/scheduled.log
else
    # Ejecutar las migraciones solo si se especifica
    if [ "$RUN_MIGRATIONS" = "true" ]; then
        python manage.py migrate
    fi

    # Ejecutar collectstatic solo si se especifica
    if [ "$RUN_COLLECTSTATIC" = "true" ]; then
        python manage.py collectstatic --no-input
    fi

    gunicorn cms.wsgi:application -c gunicorn.conf.py
fi