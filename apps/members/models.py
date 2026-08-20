from django.db import models

from apps.common.models import TimeStampedModel


class Member(TimeStampedModel):
    """A tenant. Kept deliberately separate from User - members do not log in."""

    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True)

    class Meta:
        db_table = "members"
        ordering = ("full_name",)

    def __str__(self):
        return f"{self.full_name} <{self.email}>"
