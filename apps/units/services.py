from django.utils import timezone

from .models import Unit, UnitStatus


def sync_status(unit: Unit) -> Unit:
    """Derive a unit's status from its contracts.

    A unit is occupied when a contract covers today. Anything else - no
    contracts, only future ones, only expired ones - leaves it available.
    Contracts are the source of truth, the column is just a cached view of
    them, which keeps the two from drifting apart.
    """
    today = timezone.localdate()
    occupied = unit.contracts.filter(start_date__lte=today, end_date__gte=today).exists()
    status = UnitStatus.OCCUPIED if occupied else UnitStatus.AVAILABLE

    if unit.status != status:
        unit.status = status
        unit.save(update_fields=["status", "updated_at"])
    return unit
