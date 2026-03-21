from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_otp_email(email, code):
    try:
        send_mail(
            "Your OTP Code",
            f"Your OTP is {code}",
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send OTP to {email}: {e}")
        print(f"Email error: {e}")
        return False