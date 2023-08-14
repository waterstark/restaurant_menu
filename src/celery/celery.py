from celery import Celery
from config import RABBITMQ_PASSWORD, RABBITMQ_USER, RABBITMQ_VHOST

celery = Celery(
    'tasks',
    broker=f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@app_rabbit:5672/{RABBITMQ_VHOST}',
)


@celery.task
def update_admin_xlsx():
    pass


celery.conf.beat_schedule = {
    'sync-every-15-seconds': {
        'task': 'src.tasks.update_admin_xlsx',
        'schedule': 15.0,  # Интервал в секундах
    },
}
