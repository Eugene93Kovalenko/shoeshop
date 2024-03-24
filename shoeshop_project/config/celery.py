from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

# prod or dev mode
project_mode = os.getenv('PROJECT_MODE')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'config.settings.{project_mode}')

app = Celery('config')
app.config_from_object(f'config.settings.{project_mode}', namespace='CELERY')
app.conf.update(
    broker_connection_retry_on_startup=True,
    broker_transport_options={"visibility_timeout": 1800},
)
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'test_celery_beat': {
        'task': 'orders.tasks.send_email_with_orders_count_made_yesterday',
        'schedule': crontab(minute='5', hour='0'),
    }
}
