import asyncio
from datetime import datetime, timedelta

import redis
import requests
from celery import Celery
from celery.signals import beat_init

from app import logger
from app.db import database
from app.repositories import ParcelRepository
from app.settings import settings

celery = Celery(
    'tasks',
    broker=settings.CELERY.CELERY_BROKER_URL,
    backend=settings.CELERY.CELERY_RESULT_BACKEND,
    broker_connection_retry_on_startup=True
)

redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=6379)


def get_exchange_rate():
    """
    get exchange rates
    :return:
    """
    response = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')
    data = response.json()
    return data['Valute']['USD']['Value']


@celery.task
def update_exchange_rate():
    # get exchange rates
    exchange_rate = get_exchange_rate()

    # cache to redis for EXCHANGE_RATE_UPDATE_INTERVAL_MINUTES minutes
    redis_client.set(
        'usd_exchange_rate',
        exchange_rate,
        ex=settings.EXCHANGE_RATE_UPDATE_INTERVAL_MINUTES * 60
    )

    logger.info(
        f'[{datetime.now()}] Updated USD exchange rate: {exchange_rate}'
    )


@celery.task(
    bind=True,
    # retry on error after EXCHANGE_RATE_UPDATE_INTERVAL_MINUTES minutes
    default_retry_delay=settings.EXCHANGE_RATE_UPDATE_INTERVAL_MINUTES)
def periodic_update_exchange_rate(self):
    try:
        update_exchange_rate.apply_async((), countdown=0)
    except Exception as exc:
        logger.error(f'Error updating exchange rate: {exc}')
        raise self.retry(exc=exc, countdown=300)


@beat_init.connect
def on_beat_init(**kwargs):
    result = periodic_update_exchange_rate.apply_async()
    logger.info(f'Task {periodic_update_exchange_rate.name}'
                f' scheduled with task ID: {result.id}')


@celery.task
def update_models_with_none_delivery_cost():
    session = database.get_scoped_session()
    exchange_rate = redis_client.get('usd_exchange_rate')
    logger.error(f'in redis {exchange_rate}')

    if exchange_rate:
        logger.debug('from cache')
        exchange_rate = float(exchange_rate)
    else:
        logger.debug('curl')
        exchange_rate = get_exchange_rate()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        ParcelRepository.calculate_delivery_costs(session, exchange_rate)
    )
    loop.run_until_complete(session.close())


celery.conf.beat_schedule = {
    'periodic-update-exchange-rate': {
        'task': 'app.celery_worker.periodic_update_exchange_rate',
        'schedule': timedelta(
            minutes=settings.EXCHANGE_RATE_UPDATE_INTERVAL_MINUTES
        ),  # each EXCHANGE_RATE_UPDATE_INTERVAL_MINUTES minutes
    },
    'update_models_with_none_delivery_cost': {
        'task': 'app.celery_worker.update_models_with_none_delivery_cost',
        # try to update after currency rate is refreshed
        'schedule': timedelta(seconds=10),
    },
}
