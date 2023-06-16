import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adventure_net.settings')

app = Celery('adventure_net')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()