from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

from cms.profile import base

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cms.profile.base')

app = Celery('cms')

# Configure Celery using settings from Django settings.py.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Celery beat settings
# app.conf.beat_schedule = {}

# Load tasks from all registered Django app configs.
app.autodiscover_tasks(lambda: base.INSTALLED_APPS)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')