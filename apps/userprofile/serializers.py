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

    email = serializers.EmailField(source="user.email", required=False)
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