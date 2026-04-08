from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Avatar, Profile


class AvatarSerializer(serializers.ModelSerializer):
    """
    Сериализатор аватара пользователя.

    Преобразует модель Avatar в JSON-структуру,
    ожидаемую фронтендом (Megano).

    Формат:
    {
        "src": str,  # URL изображения
        "alt": str   # описание изображения
    }
    """

    src = serializers.SerializerMethodField()

    class Meta:
        model = Avatar
        fields = ["src", "alt"]

    def get_src(self, obj):
        """
        Возвращает URL файла изображения аватара.
        """
        return obj.src.url


class ProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор профиля пользователя.

    Назначение:
    - получение данных профиля (GET /api/profile)
    - обновление профиля (POST /api/profile)

    Особенности:
    - email хранится в модели User (через source="user.email")
    - avatar возвращается как вложенный объект
    - реализована валидация:
        * обязательность fullName и email
        * уникальность телефона
        * уникальность email

    Формат ответа:
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

    email = serializers.EmailField(source="user.email", required=True)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ["fullName", "email", "phone", "avatar"]

    def get_avatar(self, obj):
        """
        Возвращает данные аватара пользователя.

        Если аватар отсутствует — возвращает дефолтное изображение.
        """
        if obj.avatar:
            return AvatarSerializer(obj.avatar).data

        return {"src": "/media/avatars/default.png", "alt": "Default avatar"}

    def validate_fullName(self, value):
        """
        Проверяет, что поле fullName не пустое и не состоит только из пробелов.
        """
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Поле fullName обязательно для заполнения."
            )
        return value

    def validate_phone(self, value):
        """
        Проверяет уникальность номера телефона.

        Допускается пустое значение.
        При обновлении исключается текущий пользователь.
        """
        if not value:
            return value

        queryset = Profile.objects.filter(phone=value)

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "Пользователь с таким телефоном уже существует."
            )

        return value

    def validate(self, attrs):
        """
        Общая валидация сериализатора.

        Проверяет:
        - обязательность email
        - уникальность email среди пользователей

        Учитывает частичное обновление (partial=True):
        если email не передан — берётся текущий.
        """
        user_data = attrs.get("user", {})
        email = user_data.get("email")

        # при partial update берём текущее значение
        if email is None and self.instance:
            email = self.instance.user.email

        if not email or not email.strip():
            raise serializers.ValidationError(
                {"email": "Поле email обязательно для заполнения."}
            )

        queryset = User.objects.filter(email=email)

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.user.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                {"email": "Пользователь с таким email уже существует."}
            )

        return attrs

    def update(self, instance, validated_data):
        """
        Обновляет профиль пользователя.

        Обновляет:
        - Profile.fullName
        - Profile.phone
        - User.email (связанная модель)

        Поддерживает частичное обновление (partial=True).
        """
        user_data = validated_data.pop("user", {})

        instance.fullName = validated_data.get("fullName", instance.fullName)
        instance.phone = validated_data.get("phone", instance.phone)
        instance.save()

        if "email" in user_data:
            instance.user.email = user_data["email"]
            instance.user.save()

        return instance
