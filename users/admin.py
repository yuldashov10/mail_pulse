from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import EmailVerificationToken, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админка для пользователей."""

    list_display = ("email", "username", "country", "is_staff")
    list_filter = ("is_staff", "is_superuser", "country")
    search_fields = ("email", "username")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Персональная информация",
            {"fields": ("username", "avatar", "phone_number", "country")},
        ),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Даты", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2"),
            },
        ),
    )
    ordering = ("email",)


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """Админка для токенов подтверждения email."""

    list_display = ("user", "token", "created_at", "expires_at", "is_valid")
    list_filter = ("created_at", "expires_at")
    search_fields = ("user__email", "token")
    readonly_fields = ("token", "created_at", "expires_at")

    def has_add_permission(self, request):
        """Запрещает добавление токенов вручную."""
        return False

    def has_change_permission(self, request, obj=None):
        """Запрещает редактирование токенов."""
        return False
