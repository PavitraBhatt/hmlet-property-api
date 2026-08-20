import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_register_returns_tokens_and_creates_staff_user(api_client):
    response = api_client.post(
        reverse("register"),
        {"email": "New.Staff@hmlet.com", "full_name": "New Staff", "password": "Sup3rSecret!"},
        format="json",
    )

    assert response.status_code == 201
    body = response.json()
    assert body["user"]["email"] == "new.staff@hmlet.com"
    assert body["user"]["is_staff"] is True
    assert body["tokens"]["access"]


def test_register_rejects_duplicate_email(api_client, staff_user):
    response = api_client.post(
        reverse("register"),
        {"email": staff_user.email, "password": "Sup3rSecret!"},
        format="json",
    )

    assert response.status_code == 400
    assert "email" in response.json()["errors"]


def test_register_rejects_weak_password(api_client):
    response = api_client.post(
        reverse("register"), {"email": "weak@hmlet.com", "password": "1234"}, format="json"
    )

    assert response.status_code == 400


def test_login_returns_a_usable_token(api_client, staff_user):
    tokens = api_client.post(
        reverse("login"), {"email": staff_user.email, "password": "Sup3rSecret!"}, format="json"
    ).json()["tokens"]

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    me = api_client.get(reverse("me"))

    assert me.status_code == 200
    assert me.json()["email"] == staff_user.email


def test_login_with_wrong_password_is_unauthorized(api_client, staff_user):
    response = api_client.post(
        reverse("login"), {"email": staff_user.email, "password": "nope"}, format="json"
    )

    assert response.status_code == 401
