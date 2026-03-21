from django.core.mail import send_mail
from django.conf import settings

def send_otp_email(email, code):
    subject = "Your OTP Code"

    message = f"Your OTP is {code}"

    html_message = f"""
    <h2>Welcome to eVoting</h2>
    <p>Your OTP code is:</p>
    <h1>{code}</h1>
    <p>This code expires in 5 minutes.</p>
    <p><b>Do not share this code.</b></p>
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
        html_message=html_message,
    )