from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, OTP


from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import OTP

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "id_number",
            "password",
            "confirm_password",
        ]

    def validate(self, data):
        # Ensure passwords match
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        # Remove confirm_password before creating user
        validated_data.pop("confirm_password", None)

        # Create the user without passing is_active
        user = User.objects.create_user(**validated_data)

        # Set user inactive until OTP verification
        user.is_active = False
        user.save()

        # Generate OTP
        otp = OTP.generate_otp(user)

        # For development: print OTP to console
        print(f"[DEV OTP] User: {user.email} | OTP: {otp.code}")

        # TODO: send OTP via email in production
        # send_mail(
        #     subject="Your Verification OTP",
        #     message=f"Your OTP is: {otp.code}. Expires in 12 hours.",
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     recipient_list=[user.email],
        # )

        return user


# ------------------------------
# OTP Verification Serializer
# ------------------------------
class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")

        try:
            otp_obj = OTP.objects.filter(
                user=user, code=data["otp"], verified=False
            ).latest("created_at")
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP")

        if not otp_obj.is_valid():
            raise serializers.ValidationError("OTP has expired")

        data["user"] = user
        data["otp_obj"] = otp_obj
        return data

    def save(self):
        user = self.validated_data["user"]
        otp_obj = self.validated_data["otp_obj"]

        # Mark user as verified/active
        user.is_verified = True
        user.is_active = True
        user.save()

        # Delete OTP so it cannot be reused
        otp_obj.delete()

        return user


# ------------------------------
# Login Serializer
# ------------------------------
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            raise serializers.ValidationError("Both email and password are required")

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password")
        if not user.is_verified:
            raise serializers.ValidationError(
                "User is not verified. Please verify your account first."
            )

        data["user"] = user
        return data
