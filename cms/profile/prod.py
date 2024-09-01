from .base import *  # noqa

DEBUG=False
AWS_STATIC_LOCATION = 'static'
STATIC_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_REGION_NAME}.digitaloceanspaces.com/{AWS_STATIC_LOCATION}/"
STATICFILES_STORAGE = 'cms.store_backends.StaticStorage'
CSRF_TRUSTED_ORIGINS = ['https://is2equipo10.me', 'https://www.is2equipo10.me']
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
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.getenv('CMS_LOG_FILENAME', '/app/logs/app.log'),
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'gunicorn.error': {
            'level': 'ERROR',
            'handlers': ['file'],
            'propagate': True,
        },
        'gunicorn.access': {
            'level': 'INFO',
            'handlers': ['file'],
            'propagate': True,
        },
    },
}

