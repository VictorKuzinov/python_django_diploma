from django.contrib import admin

from apps.order.models import DeliverySettings, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """
    Встроенное отображение позиций заказа в админке заказа.

    Используется для просмотра состава заказа прямо на странице Order.
    Редактирование, добавление и удаление позиций через inline отключены,
    так как позиции заказа должны фиксироваться в момент оформления заказа.
    """

    model = OrderItem
    extra = 0
    fields = ("product", "price", "count", "total_price")
    readonly_fields = ("product", "price", "count", "total_price")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        """
        Запрещает добавление новых позиций заказа через inline.
        """
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Кастомная административная модель заказа.

    Возможности:
    - просмотр основной информации о заказе
    - фильтрация и поиск заказов
    - просмотр состава заказа через inline
    - мягкое удаление и восстановление заказов

    Особенности:
    - стандартное удаление отключено
    - используется soft delete через поле is_deleted
    """

    inlines = [OrderItemInline]

    list_display = (
        "id",
        "user",
        "customer_name",
        "is_deleted_display",
        "delivery_type",
        "payment_type",
        "total_cost",
        "status",
        "created_at",
    )

    list_display_links = ("id", "customer_name")

    list_filter = (
        "status",
        "delivery_type",
        "payment_type",
        "is_deleted",
        "created_at",
    )

    search_fields = (
        "=id",
        "full_name",
        "email",
        "phone",
        "user__username",
    )

    ordering = ("-created_at",)
    readonly_fields = ("created_at", "total_cost")

    actions = ["soft_delete", "restore"]

    def customer_name(self, obj):
        """
        Возвращает отображаемое имя покупателя.

        Приоритет:
        1. full_name из заказа
        2. username связанного пользователя
        3. прочерк, если данные отсутствуют
        """
        if obj.full_name:
            return obj.full_name
        if obj.user:
            return obj.user.username
        return "—"

    customer_name.short_description = "Покупатель"

    def is_deleted_display(self, obj):
        """
        Отображает признак мягкого удаления заказа.
        """
        return "✅" if obj.is_deleted else "—"

    is_deleted_display.short_description = "Удалён"

    def get_actions(self, request):
        """
        Удаляет стандартное действие delete_selected из админки.
        """
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def has_delete_permission(self, request, obj=None):
        """
        Полностью запрещает физическое удаление заказов через админку.
        """
        return False

    def soft_delete(self, request, queryset):
        """
        Выполняет мягкое удаление выбранных заказов.
        """
        queryset.update(is_deleted=True)

    soft_delete.short_description = "Мягко удалить выбранные заказы"

    def restore(self, request, queryset):
        """
        Восстанавливает ранее мягко удалённые заказы.
        """
        queryset.update(is_deleted=False)

    restore.short_description = "Восстановить выбранные удалённые заказы"


@admin.register(DeliverySettings)
class DeliverySettingsAdmin(admin.ModelAdmin):
    """
    Административная модель настроек доставки.

    Используется для управления:
    - стоимостью экспресс-доставки
    - стоимостью обычной доставки
    - порогом бесплатной доставки

    Особенности:
    - в системе допускается только одна запись
    - удаление записи через админку отключено
    """

    list_display = (
        "express_delivery_price",
        "normal_delivery_price",
        "free_delivery_threshold",
    )

    def has_add_permission(self, request):
        """
        Запрещает создание более одной записи настроек доставки.
        """
        if DeliverySettings.objects.exists():
            return False
        return super().has_add_permission(request)

    def get_actions(self, request):
        """
        Удаляет стандартное действие delete_selected из админки.
        """
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def has_delete_permission(self, request, obj=None):
        """
        Полностью запрещает удаление настроек доставки через админку.
        """
        return False
