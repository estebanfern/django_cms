from .base import *  # noqa

DEBUG=False
AWS_STATIC_LOCATION = 'static'
STATIC_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_REGION_NAME}.digitaloceanspaces.com/{AWS_STATIC_LOCATION}/"
STATICFILES_STORAGE = 'cms.store_backends.StaticStorage'
