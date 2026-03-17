from django.contrib import admin
from .models import Category, Product, ProductImage, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Настройки админ-панели для модели Category."""

    list_display = (
        "id",
        "title",
        "parent",
        "is_active",
    )
    list_display_links = ("title",)
    list_filter = ("parent", "is_active",)
    ordering = ("id",)
    search_fields = ("title",)

admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Tag)