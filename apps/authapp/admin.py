from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Кастомная административная модель пользователя.

    Основные изменения:
    - отключено стандартное удаление пользователей (soft delete через is_active)
    - добавлены действия для массовой активации/деактивации
    - расширены поля отображения, фильтрации и поиска

    Используется для безопасного управления пользователями
    без физического удаления записей из базы данных.
    """

    list_display = (
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    list_display_links = ("id", "username")

    list_filter = ("groups", "is_active", "is_staff", "is_superuser", "last_login")

    search_fields = ("username", "first_name", "last_name", "email")

    ordering = ("-id",)

    actions = ["deactivate_users", "activate_users"]

    def get_actions(self, request):
        """
        Удаляет стандартное действие удаления пользователей.

        Это необходимо для реализации soft delete,
        чтобы пользователи не удалялись физически.
        """
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def has_delete_permission(self, request, obj=None):
        """
        Полностью запрещает удаление пользователей через админку.
        """
        return False

    def deactivate_users(self, request, queryset):
        """
        Массовая деактивация пользователей.

        Переводит выбранных пользователей в неактивное состояние
        (is_active = False).
        """
        queryset.update(is_active=False)

    deactivate_users.short_description = "Деактивировать выбранных пользователей"

    def activate_users(self, request, queryset):
        """
        Массовая активация пользователей.

        Переводит выбранных пользователей в активное состояние
        (is_active = True).
        """
        queryset.update(is_active=True)

    activate_users.short_description = "Активировать выбранных пользователей"
