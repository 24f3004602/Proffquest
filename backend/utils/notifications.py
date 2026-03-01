import os
import requests


def send_gchat(webhook_url, message):
    """Send a message to Google Chat via webhook."""
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
