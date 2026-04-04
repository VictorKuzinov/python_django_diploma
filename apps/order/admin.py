from django.contrib import admin

from apps.order.models import Order, OrderItem, DeliverySettings


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("product", "price", "count", "total_price")
    readonly_fields = ("product", "price", "count", "total_price")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

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
        if obj.full_name:
            return obj.full_name
        if obj.user:
            return obj.user.username
        return "—"

    customer_name.short_description = "Покупатель"

    def is_deleted_display(self, obj):
        return "✅" if obj.is_deleted else "—"

    is_deleted_display.short_description = "Удалён"

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def has_delete_permission(self, request, obj=None):
        return False

    def soft_delete(self, request, queryset):
        queryset.update(is_deleted=True)

    soft_delete.short_description = "Мягко удалить выбранные заказы"

    def restore(self, request, queryset):
        queryset.update(is_deleted=False)

    restore.short_description = "Восстановить выбранные удалённые заказы"


@admin.register(DeliverySettings)
class DeliverySettingsAdmin(admin.ModelAdmin):
    list_display = (
        "express_delivery_price",
        "normal_delivery_price",
        "free_delivery_threshold",
    )

    def has_add_permission(self, request):
        if DeliverySettings.objects.exists():
            return False
        return super().has_add_permission(request)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def has_delete_permission(self, request, obj=None):
        return False
