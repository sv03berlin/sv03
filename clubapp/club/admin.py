from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from clubapp.club.models import Membership, Resort, User


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "license")}),
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


class MembershipAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("name", "work_hours", "work_hours_boat_owner", "work_hours_club_boat_user", "work_compensation")


class ResortAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("name", "head", "is_accounting_resort")


admin.site.register(Resort, ResortAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(User, CustomUserAdmin)
