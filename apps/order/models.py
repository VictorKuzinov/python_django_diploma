from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

from apps.catalog.models import Product


class DeliveryType(models.TextChoices):
    """
    Возможные способы доставки заказа.
    """

    NORMAL = "normal", "Обычная"
    EXPRESS = "express", "Экспресс"


class OrderStatus(models.TextChoices):
    """
    Возможные статусы оплаты заказа.
    """

    NEW = "new", "Новый"
    PAID = "paid", "Оплачен"
    FAILED = "failed", "Ошибка оплаты"


class PaymentType(models.TextChoices):
    """
    Возможные способы оплаты заказа.
    """

    ONLINE = "online", "Онлайн"
    SOMEONE = "someone", "Со счета"


class Order(models.Model):
    """
    Модель заказа.

    Хранит:
    - покупателя
    - контактные данные
    - способ доставки и оплаты
    - адрес доставки
    - итоговую стоимость
    - статус оплаты
    - текст ошибки оплаты

    Особенности:
    - поддерживает мягкое удаление через is_deleted
    - сортируется по убыванию даты создания
    """

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Покупатель",
    )

    full_name = models.CharField(
        max_length=128, blank=True, default="", verbose_name="Полное имя покупателя"
    )

    email = models.EmailField(
        max_length=254, blank=True, null=True, verbose_name="Email"
    )

    phone = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Номер телефона"
    )

    delivery_type = models.CharField(
        max_length=10,
        choices=DeliveryType.choices,
        default=DeliveryType.NORMAL,
        verbose_name="Способ доставки",
    )

    payment_type = models.CharField(
        max_length=10,
        choices=PaymentType.choices,
        default=PaymentType.ONLINE,
        verbose_name="Способ оплаты",
    )

    city = models.CharField(
        max_length=128, blank=True, default="", verbose_name="Название города доставки"
    )

    address = models.TextField(blank=True, default="", verbose_name="Адрес доставки")

    status = models.CharField(
        max_length=15,
        choices=OrderStatus.choices,
        default=OrderStatus.NEW,
        verbose_name="Статус заказа",
    )

    payment_error = models.CharField(
        max_length=255, blank=True, default="", verbose_name="Текст ошибки платежа"
    )

    total_cost = models.DecimalField(
        default=0, max_digits=16, decimal_places=2, verbose_name="Итоговая сумма заказа"
    )

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата и время создания заказа"
    )

    is_deleted = models.BooleanField(default=False, verbose_name="Мягко удален")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    def __str__(self):
        """
        Строковое представление заказа.
        """
        return f"Заказ #{self.id}"


class OrderItem(models.Model):
    """
    Модель позиции заказа.

    Хранит:
    - ссылку на заказ
    - товар
    - цену товара на момент покупки
    - количество товара

    Используется для фиксации состава заказа независимо
    от последующих изменений товара в каталоге.
    """

    order = models.ForeignKey(
        Order, related_name="items", on_delete=models.CASCADE, verbose_name="Заказ"
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")

    price = models.DecimalField(
        default=0, max_digits=16, decimal_places=2, verbose_name="Цена на момент заказа"
    )

    count = models.PositiveIntegerField(default=1, verbose_name="Количество")

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    @property
    def total_price(self):
        """
        Возвращает общую стоимость позиции заказа.
        """
        return self.price * self.count

    def __str__(self):
        """
        Строковое представление позиции заказа.
        """
        return (
            f"{self.product} - {self.count} шт., стоимость: {self.price * self.count}"
        )


class DeliverySettings(models.Model):
    """
    Модель настроек доставки магазина.

    Хранит:
    - стоимость экспресс-доставки
    - стоимость обычной доставки
    - порог бесплатной доставки

    Ограничение:
    - в системе может существовать только одна запись настроек доставки
    """

    express_delivery_price = models.DecimalField(
        default=500,
        max_digits=10,
        decimal_places=2,
        verbose_name="Стоимость экспресс доставки",
    )

    normal_delivery_price = models.DecimalField(
        default=200,
        max_digits=10,
        decimal_places=2,
        verbose_name="Стоимость обычной доставки",
    )

    free_delivery_threshold = models.DecimalField(
        default=2000,
        max_digits=10,
        decimal_places=2,
        verbose_name="Порог бесплатной доставки",
    )

    class Meta:
        verbose_name = "Настройки доставки магазина"
        verbose_name_plural = "Настройки доставки магазина"

    def save(self, *args, **kwargs):
        """
        Сохраняет настройки доставки.

        Не допускает создание более одной записи в таблице.
        """
        if not self.pk and DeliverySettings.objects.exists():
            raise ValidationError("Можно создать только одну запись настроек доставки")
        return super().save(*args, **kwargs)

    def __str__(self):
        """
        Строковое представление настроек доставки.
        """
        return (
            f"Экспресс: {self.express_delivery_price} | "
            f"Обычная: {self.normal_delivery_price} | "
            f"Порог: {self.free_delivery_threshold}"
        )
