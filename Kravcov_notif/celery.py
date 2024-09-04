from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Kravcov_notif.settings')

app = Celery('Kravcov_notif')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'fetch-receptions-every-30-minutes': {
        'task': 'reminder.tasks.patient_data_chain',
        'schedule': crontab(minute='*/5'),
        'options': {'run_immediately': True},
    },
    'process-receptions-every-5-minutes': {
        'task': 'reminder.tasks.fetch_reception_call',
        'schedule': crontab(minute='*/1'),
    },
    # 'process-receptions-every-5-minutes': {
    #     'task': 'reminder.tasks.send_message_for_specific_patient_task',
    #     'schedule': crontab(minute='*/1'),
    # },
    'process-clear-models-on-12-AM': {
        'task': 'reminder.tasks.clear_models',
        'schedule': crontab(hour=0, minute=0),
        'options': {'timezone': 'Asia/Yekaterinburg'},
    },
    # 'fetch-and-process-orders-every-day-at-10-am': {
    #     'task': 'reminder.tasks.telegram_bot_task_chain',
    #     'schedule': crontab(minute='*/5'),
    # },
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
