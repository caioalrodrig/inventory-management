import os

from celery import Celery


def _get_broker_url() -> str:
    return os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")


celery_app = Celery(
    "stock_nlt",
    broker=_get_broker_url(),
    include=[
        "src.inventory.tasks",
    ],
)
