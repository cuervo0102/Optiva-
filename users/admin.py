from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display  = [
        "username", "full_name", "matricule",
        "role", "department", "is_active", "is_locked"
    ]
    list_filter   = ["role", "is_active", "is_locked", "department"]
    search_fields = ["username", "email", "full_name", "matricule"]
    actions       = ["unlock_users"]

    fieldsets = UserAdmin.fieldsets + (
        ("Informations professionnelles", {
            "fields": (
                "role", "matricule", "cnss",
                "department", "hire_date",
                "phone", "photo"
            )
        }),
        ("Security", {
            "fields": (
                "is_locked",
                "failed_login_attempts",
                "last_login_ip"
            )
        }),
    )

    def unlock_users(self, request, queryset):
        queryset.update(is_locked=False, failed_login_attempts=0)
    unlock_users.short_description = "Unlock selected accounts"