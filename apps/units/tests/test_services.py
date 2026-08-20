from datetime import date, timedelta

from apps.contracts.models import Contract
from apps.units.models import UnitStatus
from apps.units.services import sync_status


def test_sync_status_marks_unit_available_once_the_contract_ends(member, unit):
    yesterday = date.today() - timedelta(days=1)
    Contract.objects.create(
        member=member,
        unit=unit,
        start_date=yesterday - timedelta(days=30),
        end_date=yesterday,
        monthly_rent="2500.00",
        total_value="2500.00",
    )
    unit.status = UnitStatus.OCCUPIED
    unit.save(update_fields=["status"])

    sync_status(unit)

    unit.refresh_from_db()
    assert unit.status == UnitStatus.AVAILABLE
