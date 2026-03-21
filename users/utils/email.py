# users/utils/email.py
import requests
from django.conf import settings
from decouple import config
import logging

logger = logging.getLogger(__name__)

# ✅ Read API key from .env via decouple
SMTP2GO_API_KEY = config("SMTP2GO_API_KEY", default=None)

def send_otp_email(email, code):
    if not SMTP2GO_API_KEY:
        logger.error("SMTP2GO_API_KEY not set in environment!")
        return False

    url = "https://api.smtp2go.com/v3/email/send"

    payload = {
        "api_key": SMTP2GO_API_KEY,  # Use decouple config
        "to": [email],
        "sender": settings.DEFAULT_FROM_EMAIL,
        "subject": "Your OTP Code",
        "text_body": f"Welcome!\n\nYour OTP code is: {code}\n\nDo not share this code with anyone.",
    }

    headers = {
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        result = response.json()

        if result.get("data", {}).get("sent") == 1:
            logger.info(f"OTP sent successfully to {email}")
            return True
        else:
            logger.error(f"SMTP2GO API failed: {result}")
            return False
    except Exception as e:
        logger.error(f"Failed to send OTP via SMTP2GO API: {e}")
        return False