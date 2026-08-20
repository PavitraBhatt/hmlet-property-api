from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import TimeStampedModel


class UnitStatus(models.TextChoices):
    AVAILABLE = "available", "Available"
    OCCUPIED = "occupied", "Occupied"


class Unit(TimeStampedModel):
    property = models.ForeignKey(
        "properties.Property", on_delete=models.CASCADE, related_name="units"
    )
    unit_number = models.CharField(max_length=50)
    monthly_rent = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    status = models.CharField(
        max_length=20, choices=UnitStatus.choices, default=UnitStatus.AVAILABLE
    )

    class Meta:
        db_table = "units"
        ordering = ("property_id", "unit_number")
        constraints = [
            models.UniqueConstraint(
                fields=("property", "unit_number"), name="unique_unit_number_per_property"
            )
        ]

    def __str__(self):
        return f"{self.property.name} - {self.unit_number}"
