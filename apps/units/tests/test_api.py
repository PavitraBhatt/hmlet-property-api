import pytest
from django.urls import reverse

from apps.units.models import Unit, UnitStatus


def test_create_unit_under_a_property(auth_client, property_obj):
    response = auth_client.post(
        reverse("property-unit-list", args=[property_obj.pk]),
        {"unit_number": " 05-01 ", "monthly_rent": "3200.00"},
        format="json",
    )

    assert response.status_code == 201
    body = response.json()
    assert body["unit_number"] == "05-01"
    assert body["status"] == UnitStatus.AVAILABLE
    assert body["property_id"] == property_obj.pk


def test_unit_numbers_are_unique_within_a_property(auth_client, property_obj, unit):
    response = auth_client.post(
        reverse("property-unit-list", args=[property_obj.pk]),
        {"unit_number": unit.unit_number, "monthly_rent": "3200.00"},
        format="json",
    )

    assert response.status_code == 400
    assert "already exists" in str(response.json())


def test_create_unit_under_a_missing_property_is_404(auth_client):
    response = auth_client.post(
        reverse("property-unit-list", args=[404404]),
        {"unit_number": "01-01", "monthly_rent": "1000.00"},
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_units_can_be_filtered_by_status(auth_client, property_obj, unit):
    Unit.objects.create(
        property=property_obj,
        unit_number="04-13",
        monthly_rent="2600.00",
        status=UnitStatus.OCCUPIED,
    )

    available = auth_client.get(reverse("unit-list"), {"status": "available"}).json()
    occupied = auth_client.get(reverse("unit-list"), {"status": "occupied"}).json()

    assert [u["unit_number"] for u in available["results"]] == [unit.unit_number]
    assert [u["unit_number"] for u in occupied["results"]] == ["04-13"]


def test_unknown_status_filter_is_rejected(auth_client, db):
    response = auth_client.get(reverse("unit-list"), {"status": "haunted"})

    assert response.status_code == 400
