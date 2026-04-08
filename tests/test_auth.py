import json

import pytest
from django.contrib.auth.models import User
from rest_framework import status

pytestmark = pytest.mark.django_db

SIGN_UP_URL = "/api/sign-up"
SIGN_IN_URL = "/api/sign-in"
SIGN_OUT_URL = "/api/sign-out"


def test_sign_up_creates_user_and_logs_in(api_client):
    """
    Проверяем, что регистрация создаёт пользователя и возвращает 200.
    """
    payload = {
        "name": "Victor",
        "username": "new_user",
        "password": "123456",
    }

    response = api_client.post(
        SIGN_UP_URL,
        data={json.dumps(payload): ""},
        format="multipart",
    )

    assert response.status_code == status.HTTP_200_OK
    assert User.objects.filter(username="new_user").exists()

    user = User.objects.get(username="new_user")
    assert user.first_name == "Victor"


def test_sign_up_without_username_returns_500(api_client):
    """
    Проверяем, что регистрация без username возвращает 500.
    """
    payload = {
        "name": "Victor",
        "password": "123456",
    }

    response = api_client.post(
        SIGN_UP_URL,
        data={json.dumps(payload): ""},
        format="multipart",
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_sign_up_without_password_returns_500(api_client):
    """
    Проверяем, что регистрация без password возвращает 500.
    """
    payload = {
        "name": "Victor",
        "username": "new_user",
    }

    response = api_client.post(
        SIGN_UP_URL,
        data={json.dumps(payload): ""},
        format="multipart",
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_sign_up_with_duplicate_username_returns_500(api_client, user):
    """
    Проверяем, что повторная регистрация с существующим username возвращает 500.
    """
    payload = {
        "name": "Another",
        "username": user.username,
        "password": "123456",
    }

    response = api_client.post(
        SIGN_UP_URL,
        data={json.dumps(payload): ""},
        format="multipart",
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_sign_in_with_valid_credentials_returns_200(api_client, user):
    """
    Проверяем, что пользователь может войти с корректными данными.
    """
    payload = {
        "username": user.username,
        "password": "123456",
    }

    response = api_client.post(
        SIGN_IN_URL,
        data={json.dumps(payload): ""},
        format="multipart",
    )

    assert response.status_code == status.HTTP_200_OK


def test_sign_in_with_wrong_password_returns_500(api_client, user):
    """
    Проверяем, что вход с неверным паролем возвращает 500.
    """
    payload = {
        "username": user.username,
        "password": "wrong-password",
    }

    response = api_client.post(
        SIGN_IN_URL,
        data={json.dumps(payload): ""},
        format="multipart",
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_sign_in_without_username_returns_500(api_client):
    """
    Проверяем, что вход без username возвращает 500.
    """
    payload = {
        "password": "123456",
    }

    response = api_client.post(
        SIGN_IN_URL,
        data={json.dumps(payload): ""},
        format="multipart",
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_sign_in_without_password_returns_500(api_client, user):
    """
    Проверяем, что вход без password возвращает 500.
    """
    payload = {
        "username": user.username,
    }

    response = api_client.post(
        SIGN_IN_URL,
        data={json.dumps(payload): ""},
        format="multipart",
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_sign_out_returns_200(auth_client):
    """
    Проверяем, что выход пользователя возвращает 200.
    """
    response = auth_client.post(SIGN_OUT_URL, format="json")

    assert response.status_code == status.HTTP_200_OK
