from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.urls import reverse

from apps.contracts.models import Contract
from apps.units.models import UnitStatus


@pytest.fixture
def payload(member, unit):
    return {
        "member_id": member.pk,
        "unit_id": unit.pk,
        "start_date": "2026-01-01",
        "end_date": "2026-06-30",
    }


def test_create_contract_defaults_rent_and_computes_total(auth_client, payload):
    response = auth_client.post(reverse("contract-list"), payload, format="json")

    assert response.status_code == 201
    body = response.json()
    assert body["monthly_rent"] == "2500.00"
    assert body["total_value"] == "15000.00"
    assert body["unit"]["id"] == payload["unit_id"]


def test_create_contract_accepts_negotiated_rent(auth_client, payload):
    payload["monthly_rent"] = "2200.00"

    body = auth_client.post(reverse("contract-list"), payload, format="json").json()

    assert body["monthly_rent"] == "2200.00"
    assert body["total_value"] == "13200.00"


def test_overlapping_contract_is_rejected(auth_client, payload):
    assert auth_client.post(reverse("contract-list"), payload, format="json").status_code == 201

    payload["start_date"] = "2026-06-30"  # overlaps by a single day
    payload["end_date"] = "2026-12-31"
    response = auth_client.post(reverse("contract-list"), payload, format="json")

    assert response.status_code == 400
    assert "already booked" in str(response.json())
    assert Contract.objects.count() == 1


def test_back_to_back_contracts_are_allowed(auth_client, payload):
    auth_client.post(reverse("contract-list"), payload, format="json")

    payload["start_date"] = "2026-07-01"
    payload["end_date"] = "2026-12-31"
    response = auth_client.post(reverse("contract-list"), payload, format="json")

    assert response.status_code == 201
    assert Contract.objects.count() == 2


def test_end_before_start_is_rejected(auth_client, payload):
    payload["end_date"] = "2025-12-01"

    response = auth_client.post(reverse("contract-list"), payload, format="json")

    assert response.status_code == 400


def test_creating_a_current_contract_occupies_the_unit(auth_client, payload, unit):
    today = date.today()
    payload["start_date"] = str(today - timedelta(days=5))
    payload["end_date"] = str(today + timedelta(days=90))

    auth_client.post(reverse("contract-list"), payload, format="json")

    unit.refresh_from_db()
    assert unit.status == UnitStatus.OCCUPIED


def test_future_contract_leaves_the_unit_available(auth_client, payload, unit):
    payload["start_date"] = str(date.today() + timedelta(days=30))
    payload["end_date"] = str(date.today() + timedelta(days=120))

    auth_client.post(reverse("contract-list"), payload, format="json")

    unit.refresh_from_db()
    assert unit.status == UnitStatus.AVAILABLE


def test_active_filter_only_returns_running_contracts(auth_client, payload, member, unit):
    today = date.today()
    # a contract that already ended
    auth_client.post(
        reverse("contract-list"),
        {**payload, "start_date": "2020-01-01", "end_date": "2020-12-31"},
        format="json",
    )
    # and one running right now
    auth_client.post(
        reverse("contract-list"),
        {
            **payload,
            "start_date": str(today - timedelta(days=1)),
            "end_date": str(today + timedelta(days=30)),
        },
        format="json",
    )

    all_contracts = auth_client.get(reverse("contract-list")).json()
    active = auth_client.get(reverse("contract-list"), {"active": "true"}).json()

    assert all_contracts["count"] == 2
    assert active["count"] == 1
    assert active["results"][0]["is_active"] is True


def test_contract_endpoints_require_authentication(api_client, payload):
    assert api_client.get(reverse("contract-list")).status_code == 401
    assert api_client.post(reverse("contract-list"), payload, format="json").status_code == 401


def test_unknown_member_is_rejected(auth_client, payload):
    payload["member_id"] = 9999

    response = auth_client.post(reverse("contract-list"), payload, format="json")

    assert response.status_code == 400


def test_total_value_is_not_client_controlled(auth_client, payload):
    payload["total_value"] = "1.00"

    body = auth_client.post(reverse("contract-list"), payload, format="json").json()

    assert Decimal(body["total_value"]) == Decimal("15000.00")
