from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils.html import format_html

from clubapp.club.models import Membership, MembershipYear, Ressort, User


class CustomUserAdmin(UserAdmin[User]):
    readonly_fields = (
        "membership_type",
        "member_is_freed_from_work_by_age_this_year",
        "link_to_membership_years",
    )

    def get_membership_type(self, obj: User) -> MembershipYear | None:
        return obj.membership_type

    def link_to_membership_years(self, obj: User) -> str:
        membership_type = obj.membership_type
        if membership_type:
            url = reverse("admin:club_membershipyear_change", args=[membership_type.pk])
            return format_html(
                '<a href="{}">{} ({})</a>',
                url,
                membership_type,
                membership_type.year,
            )
        url = reverse("admin:club_membershipyear_changelist")
        return format_html('<a href="{}">Alle Membership Years anzeigen</a>', url)

    link_to_membership_years.short_description = "Membership Years"  # type: ignore[attr-defined]

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "email", "member_id", "openid_sub", "birthday")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_boat_owner",
                    "is_clubboat_user",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        (
            "Membership",
            {
                "fields": (
                    "membership_type",
                    "member_is_freed_from_work_by_age_this_year",
                    "link_to_membership_years",
                )
            },
        ),
    )


class MembershipAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("name", "work_hours", "work_hours_boat_owner", "work_hours_club_boat_user", "work_compensation")
    search_fields = ["name"]


class RessortAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("name",)
    filter_horizontal = ["head"]


admin.site.unregister(Group)
admin.site.register(Ressort, RessortAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(MembershipYear)
