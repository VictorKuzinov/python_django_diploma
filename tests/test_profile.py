from rest_framework import status

PROFILE_URL = "/api/profile"
PROFILE_AVATAR_URL = "/api/profile/avatar"
PROFILE_PASSWORD_URL = "/api/profile/password"


def test_get_profile_requires_auth(api_client):
    """
    Проверяем, что неавторизованный пользователь не может получить профиль.
    """
    response = api_client.get(PROFILE_URL)

    assert response.status_code in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    )


def test_get_profile_creates_profile_automatically(auth_client, user):
    """
    Проверяем, что профиль создаётся автоматически при первом GET-запросе.
    """
    from apps.userprofile.models import Profile

    assert Profile.objects.filter(user=user).count() == 0

    response = auth_client.get(PROFILE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert Profile.objects.filter(user=user).count() == 1
    assert "fullName" in response.data
    assert "email" in response.data
    assert "phone" in response.data
    assert "avatar" in response.data


def test_post_profile_updates_profile_data(auth_client):
    """
    Проверяем, что POST /profile обновляет данные профиля.
    """
    response = auth_client.post(
        PROFILE_URL,
        data={
            "fullName": "Иван Иванов",
            "email": "ivan@example.com",
            "phone": "+79990000000",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["fullName"] == "Иван Иванов"
    assert response.data["email"] == "ivan@example.com"
    assert response.data["phone"] == "+79990000000"


def test_post_profile_with_empty_fullname_returns_400(auth_client):
    """
    Проверяем, что пустой fullName не проходит валидацию.
    """
    response = auth_client.post(
        PROFILE_URL,
        data={
            "fullName": "   ",
            "email": "valid@example.com",
            "phone": "+79990000000",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "fullName" in response.data


def test_post_profile_with_empty_email_returns_400(auth_client):
    """
    Проверяем, что пустой email не проходит валидацию.
    """
    response = auth_client.post(
        PROFILE_URL,
        data={
            "fullName": "Иван Иванов",
            "email": "   ",
            "phone": "+79990000000",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data


def test_post_profile_with_duplicate_email_returns_400(
    auth_client, another_user, another_profile
):
    """
    Проверяем, что email должен быть уникальным на сайте.
    """
    response = auth_client.post(
        PROFILE_URL,
        data={
            "fullName": "Иван Иванов",
            "email": another_user.email,
            "phone": "+79990000000",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data


def test_post_profile_with_duplicate_phone_returns_400(auth_client, another_profile):
    """
    Проверяем, что телефон должен быть уникальным на сайте.
    """
    response = auth_client.post(
        PROFILE_URL,
        data={
            "fullName": "Иван Иванов",
            "email": "unique@example.com",
            "phone": another_profile.phone,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "phone" in response.data


def test_post_profile_allows_same_user_email(auth_client, user):
    """
    Проверяем, что пользователь может сохранить свой текущий email.
    """
    response = auth_client.post(
        PROFILE_URL,
        data={
            "fullName": "Иван Иванов",
            "email": user.email,
            "phone": "+79990000000",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["email"] == user.email


def test_post_profile_allows_same_user_phone(auth_client):
    """
    Проверяем, что пользователь может повторно сохранить свой текущий телефон.
    """
    auth_client.post(
        PROFILE_URL,
        data={
            "fullName": "Иван Иванов",
            "email": "ivan@example.com",
            "phone": "+79990000000",
        },
        format="json",
    )

    response = auth_client.post(
        PROFILE_URL,
        data={
            "fullName": "Иван Иванов",
            "email": "ivan@example.com",
            "phone": "+79990000000",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["phone"] == "+79990000000"


def test_get_profile_avatar_returns_200(auth_client):
    """
    Проверяем, что GET /profile/avatar возвращает данные профиля.
    """
    response = auth_client.get(PROFILE_AVATAR_URL)

    assert response.status_code == status.HTTP_200_OK
    assert "avatar" in response.data


def test_post_profile_avatar_uploads_image(auth_client, image_file):
    """
    Проверяем, что валидное изображение успешно загружается как аватар.
    """
    response = auth_client.post(
        PROFILE_AVATAR_URL,
        data={"avatar": image_file},
        format="multipart",
    )

    assert response.status_code == status.HTTP_200_OK


def test_post_profile_avatar_without_file_returns_400(auth_client):
    """
    Проверяем, что запрос без файла аватара возвращает 400.
    """
    response = auth_client.post(
        PROFILE_AVATAR_URL,
        data={},
        format="multipart",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Файл аватара не передан."


def test_post_profile_avatar_with_non_image_returns_400(auth_client, text_file):
    """
    Проверяем, что не-изображение не принимается как аватар.
    """
    response = auth_client.post(
        PROFILE_AVATAR_URL,
        data={"avatar": text_file},
        format="multipart",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Можно загружать только изображения."


def test_post_profile_avatar_with_large_file_returns_400(auth_client, large_image_file):
    """
    Проверяем, что файл больше 2 МБ отклоняется.
    """
    response = auth_client.post(
        PROFILE_AVATAR_URL,
        data={"avatar": large_image_file},
        format="multipart",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Файл слишком большой. Максимум 2 МБ."


def test_post_profile_password_changes_password(auth_client, user):
    """
    Проверяем, что пароль меняется при корректном currentPassword.
    """
    response = auth_client.post(
        PROFILE_PASSWORD_URL,
        data={
            "currentPassword": "123456",
            "newPassword": "654321",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    user.refresh_from_db()
    assert user.check_password("654321") is True


def test_post_profile_password_with_wrong_current_password_returns_400(auth_client):
    """
    Проверяем, что неверный текущий пароль возвращает 400.
    """
    response = auth_client.post(
        PROFILE_PASSWORD_URL,
        data={
            "currentPassword": "wrong-password",
            "newPassword": "654321",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Неверный текущий пароль"
