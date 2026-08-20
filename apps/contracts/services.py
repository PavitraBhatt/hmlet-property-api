"""Contract business rules.

Everything that decides *whether* a contract may exist and *what it is worth*
lives here rather than in the serializer, so the same rules apply whether a
contract is created over HTTP, from a management command or in a test.
"""

from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from dateutil.relativedelta import relativedelta
from django.db import transaction

from apps.units import services as unit_services
from apps.units.models import Unit

from .models import Contract

TWO_PLACES = Decimal("0.01")


class ContractError(Exception):
    """Raised when a contract breaks a business rule. Mapped to a 400 by the view."""


def calculate_total_value(start_date: date, end_date: date, monthly_rent: Decimal) -> Decimal:
    """Total contract value for an inclusive [start_date, end_date] period.

    Whole calendar months are charged at the full monthly rent; a leftover tail
    is pro-rated over the length of the month it falls in. So 1 Jan -> 31 Mar is
    exactly 3x rent, and 1 Jan -> 15 Feb is 1x rent + 15/28 of a month.
    """
    if end_date < start_date:
        raise ContractError("end_date must be on or after start_date.")

    rent = Decimal(monthly_rent)
    day_after_end = end_date + timedelta(days=1)

    months = 0
    cursor = start_date
    while cursor + relativedelta(months=1) <= day_after_end:
        cursor += relativedelta(months=1)
        months += 1

    total = rent * months

    leftover_days = (day_after_end - cursor).days
    if leftover_days:
        days_in_month = ((cursor + relativedelta(months=1)) - cursor).days
        total += rent * Decimal(leftover_days) / Decimal(days_in_month)

    return total.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def find_conflicting_contract(unit_id: int, start_date: date, end_date: date, exclude_id=None):
    queryset = Contract.objects.overlapping(unit_id, start_date, end_date)
    if exclude_id:
        queryset = queryset.exclude(pk=exclude_id)
    return queryset.select_related("member").first()


@transaction.atomic
def create_contract(*, member, unit_id: int, start_date, end_date, monthly_rent=None, created_by=None):
    """Create a contract, refusing to double-book the unit.

    The unit row is locked for the duration of the transaction so two requests
    racing for the same unit and period cannot both pass the overlap check.
    """
    try:
        unit = Unit.objects.select_for_update().select_related("property").get(pk=unit_id)
    except Unit.DoesNotExist:
        raise ContractError("Unit does not exist.")

    if end_date < start_date:
        raise ContractError("end_date must be on or after start_date.")

    conflict = find_conflicting_contract(unit.pk, start_date, end_date)
    if conflict:
        raise ContractError(
            f"Unit {unit.unit_number} is already booked from {conflict.start_date} "
            f"to {conflict.end_date}."
        )

    rent = monthly_rent if monthly_rent is not None else unit.monthly_rent

    contract = Contract.objects.create(
        member=member,
        unit=unit,
        start_date=start_date,
        end_date=end_date,
        monthly_rent=rent,
        total_value=calculate_total_value(start_date, end_date, rent),
        created_by=created_by,
    )

    unit_services.sync_status(unit)
    return contract
