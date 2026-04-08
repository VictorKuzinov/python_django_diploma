from django.apps import AppConfig


class OrderConfig(AppConfig):
    """
    Конфигурация приложения order.

    Отвечает за:
        - регистрацию моделей заказов и позиций заказа
        - работу с логикой оформления заказа
        - управление статусами оплаты и доставки

    Используется Django для инициализации приложения.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.order"
    verbose_name = "Заказы"
