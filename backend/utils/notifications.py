import os
import requests
import smtplib
from email.message import EmailMessage

GCHAT_URL = os.getenv("GCHAT_WEBHOOK_URL", "")


def send_gchat(webhook_url, message):
    if not webhook_url:
        print(f"[notifications] GChat webhook not configured. Message: {message}")
        return False
    try:
        response = requests.post(webhook_url, json={"text": message}, timeout=20)
        response.raise_for_status()
        return True
    except Exception as exc:
        print(f"[notifications] Failed to send GChat message: {exc}")
        return False


def send_email(to_email, subject, body):
    if not to_email:
        print("[notifications] Recipient email is missing")
        return False

    smtp_host = os.getenv("SMTP_HOST", "localhost")
    smtp_port = int(os.getenv("SMTP_PORT", "1025"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_use_tls = os.getenv("SMTP_USE_TLS", "false").strip().lower() in {"1", "true", "yes", "on"}
    email_sender = os.getenv("EMAIL_SENDER", "noreply@proffquest.local")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = email_sender
    message["To"] = to_email
    message.set_content(body)

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as smtp:
            if smtp_use_tls:
                smtp.starttls()
            if smtp_username and smtp_password:
                smtp.login(smtp_username, smtp_password)
            smtp.send_message(message)
        return True
    except Exception as exc:
        print(f"[notifications] Failed to send email: {exc}")
        return False


def notify(recipient_email, subject, body):
    send_gchat(GCHAT_URL, f"{subject}: {body}")
    send_email(recipient_email, subject, body)
