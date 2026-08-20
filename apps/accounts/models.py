from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from apps.common.models import TimeStampedModel


class UserManager(BaseUserManager):
    def create_user(self, email, password, full_name="", **extra):
        if not email:
            raise ValueError("Users must have an email address")
        extra.setdefault("is_staff", True)
        user = self.model(email=self.normalize_email(email), full_name=full_name, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, full_name="", **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        if extra.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")
        return self.create_user(email, password, full_name, **extra)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """Staff user of the property management system.

    The assignment only has staff users, so `is_staff` defaults to True and we
    drop the username field entirely - email is the login identifier.
    """

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"
        ordering = ("-created_at",)

    def __str__(self):
        return self.email
