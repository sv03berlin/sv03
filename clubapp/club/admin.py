from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from clubapp.club.models import Membership, Resort, User


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "license", "iban", "bic")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_boat_owner",
                    "is_clubboat_user",
                    "can_create_invoices",
                    "groups",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        ("Membership", {"fields": ("membership_type",)}),
    )


admin.site.register(Resort)
admin.site.register(Membership)
admin.site.register(User, CustomUserAdmin)
