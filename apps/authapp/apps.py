from django.apps import AppConfig


class AuthappConfig(AppConfig):
    """
    Конфигурация приложения authapp.

    Используется для регистрации приложения в Django.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.authapp"
