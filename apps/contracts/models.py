from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.common.models import TimeStampedModel


class ContractQuerySet(models.QuerySet):
    def active(self, on=None):
        """Contracts running on a given day (defaults to today)."""
        on = on or timezone.localdate()
        return self.filter(start_date__lte=on, end_date__gte=on)

    def overlapping(self, unit_id, start_date, end_date):
        """Two closed date ranges overlap when each starts before the other ends."""
        return self.filter(unit_id=unit_id, start_date__lte=end_date, end_date__gte=start_date)


class Contract(TimeStampedModel):
    member = models.ForeignKey("members.Member", on_delete=models.PROTECT, related_name="contracts")
    unit = models.ForeignKey("units.Unit", on_delete=models.PROTECT, related_name="contracts")
    start_date = models.DateField()
    end_date = models.DateField()
    monthly_rent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Defaults to the unit's rent when not supplied.",
    )
    total_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Derived from the contract period and monthly rent - never set by the client.",
    )
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contracts",
    )

    objects = ContractQuerySet.as_manager()

    class Meta:
        db_table = "contracts"
        ordering = ("-start_date", "-id")
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_date__gte=models.F("start_date")),
                name="contract_end_date_after_start_date",
            )
        ]
        indexes = [
            models.Index(fields=("unit", "start_date", "end_date"), name="contract_unit_period_ix")
        ]

    def __str__(self):
        period = f"{self.start_date} to {self.end_date}"
        return f"{self.member.full_name} @ {self.unit.unit_number} ({period})"

    @property
    def is_active(self):
        return self.start_date <= timezone.localdate() <= self.end_date
