import os
from celery import Celery
from datetime import timedelta

def make_celery():
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    celery = Celery(
        __name__,
        broker=redis_url,
        backend=redis_url,
        include=["app.tasks"],  # 👈 Ensure Celery preloads tasks
    )

    # 🔹 Configure periodic tasks
    # celery.conf.beat_schedule = {
    #     "print-every-30-seconds": {
    #         "task": "app.tasks.print_time",
    #         "schedule": timedelta(seconds=30),
    #     },
    # }

    return celery

celery = make_celery()
