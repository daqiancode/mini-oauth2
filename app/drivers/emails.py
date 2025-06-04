import smtplib
from email.mime.text import MIMEText
import asyncio

from app.config import settings

async def send_email(to,subject, body):
    await asyncio.to_thread(send_email_sync, to, subject, body)
# import ssl
def send_email_sync(to,subject, body):
    msg = MIMEText(body, 'html')
    msg['Subject'] = subject
    msg['From'] = settings.EMAIL_FROM or settings.EMAIL_USERNAME
    msg['To'] = to
    # context=ssl.create_default_context()
    # context.check_hostname = False
    # context.verify_mode = ssl.CERT_NONE
    if settings.EMAIL_SSL:
        with smtplib.SMTP_SSL(settings.EMAIL_HOST, int(settings.EMAIL_PORT), timeout=30) as server:
            server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            server.send_message(msg)
    else:
        with smtplib.SMTP(settings.EMAIL_HOST, int(settings.EMAIL_PORT), timeout=30) as server:
            server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            server.send_message(msg)

