from datetime import date

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def staff_user(db):
    return get_user_model().objects.create_user(
        email="ops@hmlet.com", password="Sup3rSecret!", full_name="Ops Staff"
    )


@pytest.fixture
def auth_client(api_client, staff_user):
    api_client.force_authenticate(user=staff_user)
    return api_client


@pytest.fixture
def property_obj(db):
    from apps.properties.models import Property

    return Property.objects.create(name="Cove Somerset", address="12 Somerset Rd, Singapore")


@pytest.fixture
def unit(property_obj):
    from apps.units.models import Unit

    return Unit.objects.create(property=property_obj, unit_number="04-12", monthly_rent="2500.00")


@pytest.fixture
def member(db):
    from apps.members.models import Member

    return Member.objects.create(full_name="Aditi Rao", email="aditi@example.com")


@pytest.fixture
def contract(member, unit):
    from apps.contracts.services import create_contract

    return create_contract(
        member=member,
        unit_id=unit.pk,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
    )
