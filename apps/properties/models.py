from django.db import models

from apps.common.models import TimeStampedModel


class Property(TimeStampedModel):
    name = models.CharField(max_length=200)
    address = models.TextField()
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="properties",
    )

    class Meta:
        db_table = "properties"
        verbose_name_plural = "properties"
        ordering = ("-created_at",)

    def __str__(self):
        return self.name
