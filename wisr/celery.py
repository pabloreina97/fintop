from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

# establecer el valor predeterminado de Django para la aplicación de Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wisr.settings')

app = Celery('wisr')

# Usar la configuración de Django para configurar Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Cargar tareas definidas en cada aplicación
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Programar tareas periódicas
app.conf.beat_schedule = {
    'sync-daily': {
        'task': 'wisr.tasks.sync_transactions',
        'schedule': 300.0
        # 'schedule': crontab()
    },
}
