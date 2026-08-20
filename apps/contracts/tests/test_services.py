from datetime import date
from decimal import Decimal

import pytest

from apps.contracts.services import ContractError, calculate_total_value


@pytest.mark.parametrize(
    "start,end,rent,expected",
    [
        # exactly one year
        (date(2026, 1, 1), date(2026, 12, 31), "2500.00", "30000.00"),
        # exactly one month
        (date(2026, 3, 1), date(2026, 3, 31), "1800.00", "1800.00"),
        # a month that does not start on the 1st still counts as one month
        (date(2026, 3, 15), date(2026, 4, 14), "1800.00", "1800.00"),
        # one month + 15 days pro-rated over a 28 day February
        (date(2026, 1, 1), date(2026, 2, 15), "2800.00", "4300.00"),
        # single day
        (date(2026, 6, 10), date(2026, 6, 10), "3000.00", "100.00"),
    ],
)
def test_total_value(start, end, rent, expected):
    assert calculate_total_value(start, end, Decimal(rent)) == Decimal(expected)


def test_total_value_rejects_backwards_period():
    with pytest.raises(ContractError):
        calculate_total_value(date(2026, 5, 1), date(2026, 4, 1), Decimal("1000"))
