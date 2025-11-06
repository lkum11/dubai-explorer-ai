# -------------------------------------------------
# Celery example tasks.
# Demonstrates async execution and SendGrid integration.
# -------------------------------------------------

from app.celery_app import celery
from app.email_utils import send_email
from datetime import datetime, timezone

@celery.task
def add_numbers(a, b):
    print(f"Adding numbers: {a} + {b}")
    return a + b

# @celery.task
# def print_time():
#     now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
#     print(f"[Scheduled Task] Current UTC time: {now}")
#     return now

@celery.task
def send_welcome_email(to_email, name):
    subject = "Welcome to Flask + Celery + SendGrid!"
    content = f"Hi {name},\n\nThis is a test email from your Flask-Celery project.\n\nCheers,\nLovely's Backend 🚀"
    print("*"*100)
    status = send_email(to_email, subject, content)
    return status