from django.contrib.auth import update_session_auth_hash
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import Profile, Avatar
from .serializers import ProfileSerializer


class ProfileView(APIView):
    """
    API для работы с профилем пользователя.

    Endpoint:
        GET  /api/profile  — получить данные профиля
        POST /api/profile  — обновить данные профиля

    Доступ:
        Только для авторизованных пользователей.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Получение профиля текущего пользователя.

        Если профиль отсутствует, он создаётся автоматически.

        Возвращает JSON:
        {
            "fullName": str,
            "email": str,
            "phone": str,
            "avatar": {
                "src": str,
                "alt": str
            }
        }
        """

        profile, created = Profile.objects.get_or_create(
            user=request.user,
            defaults={"fullName": request.user.username}
        )

        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def post(self, request):
        """
        Обновление данных профиля пользователя.

        Принимает JSON:
        {
            "fullName": str,
            "email": str,
            "phone": str
        }

        Возвращает:
        200 — профиль успешно обновлён
        400 — ошибка валидации данных
        """

        profile, created = Profile.objects.get_or_create(
            user=request.user,
            defaults={"fullName": request.user.username}
        )

        serializer = ProfileSerializer(
            profile,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileAvatarView(APIView):
    """
    API для загрузки и получения аватара пользователя.

    Endpoint:
        POST /api/profile/avatar — загрузка нового аватара
        GET  /api/profile/avatar — получение данных профиля

    Ограничения:
        размер файла аватара не должен превышать 2 МБ.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Загрузка нового аватара пользователя.

        Ожидает multipart/form-data с файлом "avatar".

        Проверяет:
        - наличие файла
        - размер файла (не более 2 МБ)

        Возвращает:
        200 — аватар успешно загружен
        400 — ошибка загрузки
        """

        profile, created = Profile.objects.get_or_create(
            user=request.user,
            defaults={"fullName": request.user.username}
        )

        avatar_file = request.FILES.get("avatar")

        if not avatar_file:
            return Response(
                data={"error": "Файл аватара не передан."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # проверка, что файл изображение
        if not avatar_file.content_type.startswith("image/"):
            return Response(
                data={"error": "Можно загружать только изображения."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ограничение из ТЗ: не более 2 МБ
        if avatar_file.size > 2 * 1024 * 1024:
            return Response(
                {"error": "Файл слишком большой. Максимум 2 МБ."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # если у профиля уже есть аватар — обновляем его
        if profile.avatar:
            profile.avatar.src = avatar_file
            profile.avatar.alt = avatar_file.name
            profile.avatar.save()
        else:
            avatar = Avatar.objects.create(
                src=avatar_file,
                alt=avatar_file.name
            )
            profile.avatar = avatar
            profile.save()

        return Response(status=status.HTTP_200_OK)

    def get(self, request):
        """
        Получение данных профиля вместе с аватаром.
        """

        profile, created = Profile.objects.get_or_create(
            user=request.user,
            defaults={"fullName": request.user.username}
        )

        serializer = ProfileSerializer(profile)
        return Response(serializer.data)


class ProfilePasswordView(APIView):
    """
    API для смены пароля пользователя.

    Endpoint:
        POST /api/profile/password

    Принимает JSON:
    {
        "currentPassword": str,
        "newPassword": str
    }

    Доступ:
        Только для авторизованных пользователей.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Смена пароля пользователя.

        Проверяет корректность текущего пароля
        и устанавливает новый пароль.

        Возвращает:
        200 — пароль успешно изменён
        400 — текущий пароль неверный
        """

        current_password = request.data.get("currentPassword")
        new_password = request.data.get("newPassword")

        if not request.user.check_password(current_password):
            return Response(
                {"error": "Неверный текущий пароль"},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.user.set_password(new_password)
        request.user.save()

        # обновляем сессию, чтобы пользователь не разлогинился
        update_session_auth_hash(request, request.user)

        return Response(status=status.HTTP_200_OK)