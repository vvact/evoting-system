from django.contrib import admin
from .models import User, OTP


# Existing UserAdmin with OTP generation
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "middle_name",
        "last_name",
        "email",
        "id_number",
        "is_verified",
        "has_voted",
    )
    search_fields = ("email", "id_number")

    def save_model(self, request, obj, form, change):
        """
        Generate OTP when a new user is created from admin.
        """
        is_new = obj._state.adding
        super().save_model(request, obj, form, change)
        if is_new:
            otp = OTP.generate_otp(obj)
            print(f"[ADMIN-DEV OTP] User: {obj.email} | OTP: {otp.code}")


# Register OTP model for visibility in admin
@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "created_at", "expires_at", "is_valid_display")
    search_fields = ("user__email", "code")
    list_filter = ("created_at", "expires_at")

    def is_valid_display(self, obj):
        return obj.is_valid()

    is_valid_display.boolean = True
    is_valid_display.short_description = "Valid?"
