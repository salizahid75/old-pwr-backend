from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from power.utils import getVerificationTokenDateTime


class UserManager(BaseUserManager):

    def create_user(self, email, name, password, **other_fields):

        if not email:
            raise ValueError("email address is required!")
        if not name:
            raise ValueError("name is required!")
        if not password:
            raise ValueError("password is required!")

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **other_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, name, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError("Superuser must be assigned to is_staff=True")
        if other_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must be assigned to is_superuser=True")

        user = self.create_user(email, name, password, **other_fields)

        return user


class MainUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    created = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f'{self.name}={self.email}'


class VerificationToken(models.Model):
    user = models.ForeignKey(
        MainUser, on_delete=models.CASCADE, related_name="token")
    code = models.CharField(max_length=5)
    token_type = models.CharField(max_length=5)
    expires = models.DateTimeField(default=getVerificationTokenDateTime)
