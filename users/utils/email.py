from django.core.mail import send_mail
from django.conf import settings

def send_otp_email(email, code):
    subject = "Your OTP Code"
    message = f"""
Welcome!

Your OTP code is: {code}

This code will expire soon.

Do not share this code with anyone.
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,  # ✅ prints errors to console if something fails
    )