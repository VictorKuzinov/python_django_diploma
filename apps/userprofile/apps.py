from django.apps import AppConfig


class UserprofileConfig(AppConfig):
    """
    Конфигурация приложения userprofile.

    Отвечает за:
    - хранение и управление профилями пользователей
    - работу с дополнительными данными пользователя (ФИО, телефон)
    - загрузку и хранение аватаров

    Используется Django для инициализации приложения.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.userprofile"
    verbose_name = "Профили покупателей"
