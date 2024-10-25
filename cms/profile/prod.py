from .base import *  # noqa

DEBUG=False
AWS_STATIC_LOCATION = 'static'
STATIC_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_REGION_NAME}.digitaloceanspaces.com/{AWS_STATIC_LOCATION}/"
STATICFILES_STORAGE = 'cms.store_backends.StaticStorage'
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default=['https://is2equipo10.me', 'https://www.is2equipo10.me', 'https://stripe.com'])
# CSRF_TRUSTED_ORIGINS = config('DJANGO_ALLOWED_HOSTS', default='localhost').split(',')
# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.getenv('CMS_LOG_FILENAME', '/app/logs/app.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'level': 'INFO',
            'handlers': ['file', 'console'],
            'propagate': True,
        },
        'gunicorn.error': {
            'level': 'ERROR',
            'handlers': ['file', 'console'],
            'propagate': True,
        },
        'gunicorn.access': {
            'level': 'INFO',
            'handlers': ['file', 'console'],
            'propagate': True,
        },
        # Este logger captura todos los mensajes no capturados por loggers específicos
        '': {
            'level': 'INFO',
            'handlers': ['file', 'console'],
            'propagate': False,
        },
    },
}

# REDIS CACHE
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{config('REDIS_HOST', default='localhost:6379')}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}
