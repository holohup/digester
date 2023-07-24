from celery import shared_task
from django.conf import settings
from kombu import Connection, Queue


@shared_task
def publish_to_rabbitmq(method, body):
    exchange = ''
    routing_key = 'parser'

    with Connection(settings.CELERY_BROKER_URL) as conn:
        channel = conn.channel()
        queue = Queue(
            routing_key, channel=channel, durable=True, auto_delete=False
        )
        queue.declare()
        producer = conn.Producer(serializer='json')
        producer.publish(
            body,
            exchange=exchange,
            routing_key=routing_key,
            headers={'method': method},
        )
