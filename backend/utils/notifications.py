import os
import smtplib
from email.message import EmailMessage
import requests


def _smtp_config():
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    sender = os.getenv("EMAIL_SENDER", username or "no-reply@example.com")
    return host, port, username, password, use_tls, sender


def send_email(to_address, subject, body, html_body=None):
    host, port, username, password, use_tls, sender = _smtp_config()
    if not host:
        print(f"[notifications] SMTP not configured. Would email {to_address}: {subject}")
        return False

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.set_content(body)
    if html_body:
        msg.add_alternative(html_body, subtype="html")

    try:
        with smtplib.SMTP(host, port, timeout=30) as server:
            if use_tls:
                server.starttls()
            if username and password:
                server.login(username, password)
            server.send_message(msg)
        return True
    except Exception as exc:
        print(f"[notifications] Failed to send email to {to_address}: {exc}")
        return False


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


def send_sms(phone_number, message):
    print(f"[notifications] SMS not configured. Would SMS {phone_number}: {message}")
    return False
