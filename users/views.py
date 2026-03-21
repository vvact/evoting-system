# users/views.py
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .models import OTP
from .serializers import RegisterSerializer, OTPVerifySerializer, LoginSerializer

# ✅ Email utility
from users.utils.email import send_otp_email

import logging

logger = logging.getLogger(__name__)

User = get_user_model()

# ------------------------------
# Register Endpoint
# ------------------------------
@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()

        # Set inactive until OTP verified
        user.is_active = False
        user.save()

        # Get latest OTP
        otp = OTP.objects.filter(user=user).last()

        # ✅ Send OTP safely
        if not send_otp_email(user.email, otp.code):
            logger.warning(f"Failed to send OTP to {user.email}. User still created.")


# ------------------------------
# OTP Verify Endpoint
# ------------------------------
class OTPVerifyView(generics.GenericAPIView):
    serializer_class = OTPVerifySerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["otp"]

        try:
            user = User.objects.get(email=email)
            otp = OTP.objects.filter(user=user, code=code, verified=False).last()

            if not otp:
                return Response(
                    {"detail": "Invalid OTP."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not otp.is_valid():
                return Response(
                    {"detail": "OTP has expired. Please request a new one."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Mark OTP as verified
            otp.verified = True
            otp.save()

            # Activate user
            user.is_active = True
            user.is_verified = True
            user.save()

            return Response(
                {"message": "Account verified successfully"},
                status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )


# ------------------------------
# Resend OTP Endpoint
# ------------------------------
class ResendOTPView(generics.GenericAPIView):
    serializer_class = OTPVerifySerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")

        if not email:
            return Response(
                {"detail": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)

            # Generate new OTP
            otp = OTP.generate_otp(user)

            # ✅ Send OTP safely
            if send_otp_email(user.email, otp.code):
                return Response(
                    {"detail": "A new OTP has been sent."},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"detail": "OTP could not be sent. Try again later."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )


# ------------------------------
# Login Endpoint
# ------------------------------
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return Response(
            {
                "success": True,
                "access": str(access),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "middle_name": getattr(user, "middle_name", ""),
                    "last_name": user.last_name,
                    "id_number": getattr(user, "id_number", ""),
                },
            },
            status=status.HTTP_200_OK,
        )