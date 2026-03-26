import json

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class SignInView(APIView):
    """
    API для авторизации пользователя.

    Endpoint:
        POST /api/sign-in

    Ожидает данные пользователя в формате,
    который отправляет фронтенд Megano.

    Возвращает:
        200 — успешная авторизация
        500 — ошибка авторизации
    """

    def post(self, request):
        """
        Выполняет вход пользователя в систему.

        Извлекает username и password из тела запроса,
        проверяет пользователя через authenticate()
        и создаёт сессию через login().
        """
        try:
            if not request.POST:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            serialized_data = list(request.POST.keys())[0]
            user_data = json.loads(serialized_data)

            username = user_data.get("username")
            password = user_data.get("password")

            if not username or not password:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            user = authenticate(request, username=username, password=password)

            if user is None:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            login(request, user)
            return Response(status=status.HTTP_200_OK)

        except Exception:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SignUpView(APIView):
    """
    API для регистрации пользователя.

    Endpoint:
        POST /api/sign-up

    Ожидает данные пользователя в формате,
    который отправляет фронтенд Megano.

    Возвращает:
        200 — пользователь успешно зарегистрирован
        500 — ошибка регистрации
    """

    def post(self, request):
        """
        Регистрирует нового пользователя.

        Создаёт пользователя в системе, при наличии имени
        записывает его в first_name, затем авторизует
        нового пользователя через login().
        """
        print(request.data)
        print(type(request.data))
        try:
            if not request.data:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            serialized_data = list(request.data.keys())[0]
            user_data = json.loads(serialized_data)

            name = user_data.get("name")
            username = user_data.get("username")
            password = user_data.get("password")

            if not username or not password:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            user = User.objects.create_user(
                username=username,
                password=password
            )

            if name:
                user.first_name = name
                user.save()

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return Response(status=status.HTTP_200_OK)

            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SignOutView(APIView):
    """
    API для выхода пользователя из системы.

    Endpoint:
        POST /api/sign-out

    Возвращает:
        200 — успешный выход пользователя
    """

    def post(self, request):
        """
        Завершает пользовательскую сессию.
        """
        logout(request)
        return Response(status=status.HTTP_200_OK)