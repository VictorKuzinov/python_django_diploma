from django.apps import AppConfig


class PaymentConfig(AppConfig):
    """
    Конфигурация приложения payment.

    Отвечает за:
    - обработку логики оплаты заказов
    - изменение статуса заказа (PAID / FAILED)
    - очистку корзины после успешной оплаты

    Используется Django для инициализации приложения.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.payment"
