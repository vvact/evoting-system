from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .managers import UserManager
from datetime import timedelta
import random


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50)
    id_number = models.CharField(max_length=20, unique=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    has_voted = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "id_number"]

    objects = UserManager()

    def __str__(self):
        return self.email


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP {self.code} for {self.user.email} (verified={self.verified})"

    def is_valid(self):
        """Check if OTP is still valid."""
        return timezone.now() <= self.expires_at and not self.verified

    @staticmethod
    def generate_otp(user, expiry_hours=12):
        """Generate a new OTP for a user with optional expiry in hours (default 12)."""
        # Delete any unverified old OTPs
        OTP.objects.filter(user=user, verified=False).delete()

        # Generate zero-padded 6-digit OTP
        code = f"{random.randint(0, 999999):06d}"
        expires = timezone.now() + timedelta(hours=expiry_hours)
        otp = OTP.objects.create(user=user, code=code, expires_at=expires)
        return otp
