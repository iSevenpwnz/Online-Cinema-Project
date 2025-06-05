import os
from celery import Celery

celery_app = Celery(
    "celery_worker",
    broker=f"redis://{os.environ.get('REDIS_HOST')}:{os.environ.get('REDIS_PORT')}/0",
    backend=f"redis://{os.environ.get('REDIS_HOST')}:{os.environ.get('REDIS_PORT')}/0",
)

import celery_config.tasks  # noqa: E402, F401

celery_app.config_from_object("celery_config.celeryconfig")  # type: ignore
