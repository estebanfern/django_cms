from .base import *  # noqa

DEBUG=False
AWS_STATIC_LOCATION = 'static'
STATIC_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_REGION_NAME}.digitaloceanspaces.com/{AWS_STATIC_LOCATION}/"
STATICFILES_STORAGE = 'cms.store_backends.StaticStorage'

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

