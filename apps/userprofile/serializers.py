from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Avatar, Profile


class AvatarSerializer(serializers.ModelSerializer):
    """
    Сериализатор аватара пользователя.

    Преобразует объект Avatar в JSON-структуру,
    ожидаемую фронтендом Megano.
    """

    src = serializers.SerializerMethodField()

    class Meta:
        model = Avatar
        fields = ["src", "alt"]

    def get_src(self, obj):
        """
        Возвращает полный URL изображения аватара.
        """
        return obj.src.url


class ProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор профиля пользователя.

    Используется для:
    - получения данных профиля
    - обновления имени, телефона и email

    Поле email берётся из связанной модели User.
    Поле avatar возвращается как вложенный объект.
    """

    email = serializers.EmailField(source="user.email", required=True)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ["fullName", "email", "phone", "avatar"]

    def get_avatar(self, obj):
        """
        Возвращает данные аватара пользователя.

        Если у пользователя аватар не задан,
        возвращает объект с дефолтным изображением.
        """
        if obj.avatar:
            return AvatarSerializer(obj.avatar).data

        return {
            "src": "/media/avatars/default.png",
            "alt": "Default avatar"
        }

    def validate_fullName(self, value):
        """
            Проверяет, что полное имя заполнено.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Поле fullName обязательно для заполнения.")
        return value

    def validate_phone(self, value):
        """
            Проверяет уникальность телефона.
        """
        if not value:
            return value
        queryset = Profile.objects.filter(phone=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Пользователь с таким телефоном уже существует.")
        return value

    def validate(self, attrs):
        """
            Проверяет обязательность и уникальность email.
        """
        user_data = attrs.get("user", {})
        email = user_data.get("email")
        if email is None and self.instance:
            email = self.instance.user.email

        if not email or not email.strip():
            raise serializers.ValidationError({
                "email": "Поле email обязательно для заполнения."
            })
        queryset = User.objects.filter(email=email)

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.user.pk)

        if queryset.exists():
            raise serializers.ValidationError({"email": "Пользователь с таким email уже существует."})
        return attrs

    def update(self, instance, validated_data):
        """
        Обновляет данные профиля пользователя.

        Обновляет поля модели Profile:
        - fullName
        - phone

        И поле email в связанной модели User.
        """
        user_data = validated_data.pop("user", {})

        instance.fullName = validated_data.get("fullName", instance.fullName)
        instance.phone = validated_data.get("phone", instance.phone)
        instance.save()

        if "email" in user_data:
            instance.user.email = user_data["email"]
            instance.user.save()

        return instance
