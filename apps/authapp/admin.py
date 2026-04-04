from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
        "is_active",
        "is_staff",
        "is_superuser"
    )
    list_display_links = ("id", "username")
    list_filter = (
        "groups",
        "is_active",
        "is_staff",
        "is_superuser",
        "last_login"
    )
    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email"
    )
    ordering = ("-id",)
    
    actions = ["deactivate_users", "activate_users"]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def has_delete_permission(self, request, obj=None):
        return False

    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)

    deactivate_users.short_description = "Деактивировать выбранных пользователей"

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)

    activate_users.short_description = "Активировать выбранных пользователей"
