# users/managers.py
from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):

    def create_user(
        self, email, first_name, last_name, id_number, middle_name=None, password=None
    ):
        """
        Creates and saves a User with the given email, first name, last name,
        optional middle name, ID number, and password.
        """
        if not email:
            raise ValueError("Users must have an email")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            first_name=first_name,
            middle_name=middle_name,  # <-- added middle_name support
            last_name=last_name,
            id_number=id_number,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email,
        password,
        first_name="Admin",
        middle_name="",
        last_name="User",
        id_number="00000000",
    ):
        """
        Creates and returns a superuser.
        Django calls this during `createsuperuser` command.
        """
        user = self.create_user(
            email=email,
            first_name=first_name,
            middle_name=middle_name,  # <-- added middle_name support
            last_name=last_name,
            id_number=id_number,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_verified = True
        user.save(using=self._db)
        return user
