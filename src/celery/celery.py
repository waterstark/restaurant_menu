import asyncio

from celery import Celery
from src.celery.tasks import comparation
from src.config import RABBITMQ_PASSWORD, RABBITMQ_USER, RABBITMQ_VHOST

celery = Celery(
    'tasks',
    broker=f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_VHOST}:5672',
)


@celery.task
def update_admin_xlsx():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(comparation())


# update_admin_xlsx.delay()
celery.conf.beat_schedule = {
    'sync-every-15-seconds': {
        'task': 'src.celery.celery.update_admin_xlsx',
        'schedule': 15.0,  # Интервал в секундах
    },
}
