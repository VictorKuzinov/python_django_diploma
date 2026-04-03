from django.contrib import admin
from django.utils import timezone

from .models import (
    Category,
    Product,
    ProductImage,
    Tag,
    Review,
    Specification,
    Sale,
)

admin.site.register(ProductImage)
admin.site.register(Tag)
admin.site.register(Specification)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Настройки админ-панели для модели Category."""

    list_display = (
        "id",
        "title",
        "parent",
        "is_active",
    )
    list_display_links = ("title", "id")
    list_filter = ("parent", "is_active",)
    ordering = ("title",)
    search_fields = ("title",)

    actions = ["soft_delete", "restore"]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def soft_delete(self, request, queryset):
        queryset.update(is_active=False)

    soft_delete.short_description = "Мягко удалить выбранные категории"

    def restore(self, request, queryset):
        queryset.update(is_active=True)

    restore.short_description = "Восстановить выбранные удалённые категории"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "category",
        "is_deleted_display",
        "price",
        "count",
        "rating",
    )

    list_filter = (
        "category",
        "free_delivery",
        "limited_edition",
        "is_deleted",
        "category__is_active",
    )

    search_fields = (
        "title",
        "description",
    )

    list_display_links = ("id", "title")
    ordering = ("-id",)

    actions = ["soft_delete", "restore"]

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

    soft_delete.short_description = "Мягко удалить выбранные товары"

    def restore(self, request, queryset):
        queryset.update(is_deleted=False)

    restore.short_description = "Восстановить выбранные удалённые товары"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_select_related = ("product",)

    list_display = (
        "id",
        "product",
        "rate",
        "author",
        "short_text",
        "date",
    )
    list_display_links = ("id", "author")
    list_filter = (
        "rate",
        "product",
        "product__category",
        "date",
    )
    search_fields = (
        "author",
        "email",
        "text",
        "product__title"
    )
    ordering = ("-date",)

    def short_text(self, obj):
        if len(obj.text) > 30:
            return f"{obj.text[:30]}..."
        return obj.text

    short_text.short_description = "Текст отзыва"


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):

    list_select_related = ("product",)

    list_display = (
        "id",
        "title",
        "product",
        "product_price",
        "sale_price",
        "discount_amount",
        "is_active",
        "date_from",
        "date_to",
        "created_at",
    )
    list_display_links = ("id", "title")
    list_filter = (
        "date_from",
        "date_to",
        "created_at"
    )
    search_fields = (
        "title",
        "product__title",
        "product__category__title"
    )
    ordering = ("-created_at",)

    def is_active(self, obj):
        date_now = timezone.now()
        return obj.date_from <= date_now <= obj.date_to

    is_active.boolean = True
    is_active.short_description = "Активна"

    def product_price(self, obj):
        return obj.product.price

    product_price.short_description = "Старая цена"

    def discount_amount(self, obj):
        return obj.product.price - obj.sale_price

    discount_amount.short_description = "Скидка"

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def has_delete_permission(self, request, obj=None):
        return False