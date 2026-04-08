from django.apps import AppConfig


class BasketConfig(AppConfig):
    """
    Конфигурация приложения basket.

    Используется для регистрации приложения в Django.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.basket"
