from celery import Celery
from app import create_app
import os

def make_celery(app_name=__name__):
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    return Celery(app_name, broker=redis_url, backend=redis_url)

celery = make_celery()

app = create_app()
celery.conf.update(app.config)

@celery.task
def add_numbers(a, b):
    print(f"Adding numbers: {a} + {b}")
    return a + b
