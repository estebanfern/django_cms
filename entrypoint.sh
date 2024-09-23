#!/bin/sh

if [ "$1" = "workers" ]; then
    # shift  # Remover "celery" del argumento
    # celery "$@"  # Ejecutar el comando de celery con los argumentos restantes
    echo "Executing workers"
    celery -A cms worker -l info -f /app/logs/workers.log
elif [ "$1" = "scheduled" ]; then
    echo "Executing scheduled tasks"
    celery -A cms beat -l info -f /app/logs/scheduled.log
else
    echo "Executing app"
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