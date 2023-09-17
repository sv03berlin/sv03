from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.db.models.query import QuerySet
from django.http import HttpRequest

from clubapp.club.importer import send_new_password
from clubapp.club.models import Membership, Ressort, User


@admin.action(description="neues Passworz Zusenden")
def make_send_new_password(modeladmin: admin.ModelAdmin[User], request: HttpRequest, queryset: QuerySet["User"]) -> None:
    for user in queryset:
        send_new_password(user)


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "username",
                    "password",
                )
            },
        ),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
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
        ("Membership", {"fields": ("membership_type", "membership_id", "license")}),
    )
    autocomplete_fields = ["membership_type"]
    search_fields = ["membership_id", "first_name", "last_name", "email"]
    list_display = ("__str__", "membership_id", "is_staff", "is_active", "is_superuser", "is_boat_owner", "is_clubboat_user")
    actions = [make_send_new_password]


class MembershipAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("name", "work_hours", "work_hours_boat_owner", "work_hours_club_boat_user", "work_compensation")
    search_fields = ["name"]


class RessortAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("name", "head", "is_accounting_ressort")
    autocomplete_fields = ["head"]


admin.site.unregister(Group)
admin.site.register(Ressort, RessortAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(User, CustomUserAdmin)
