# -------------------------------------------------
# Optional utility for sending emails via SendGrid.
# Currently used by Celery example task for testing.
# -------------------------------------------------

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email(to_email, subject, content):
    api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("SENDER_EMAIL")

    if not api_key or not from_email:
        raise RuntimeError("Missing SENDGRID_API_KEY or SENDER_EMAIL env var")

    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        plain_text_content=content,
    )

    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        print(f"📧 Email sent to {to_email} (status={response.status_code})")
        return response.status_code
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return None
