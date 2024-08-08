from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from clubapp.club.models import Membership, MembershipYear, Ressort, User


class CustomUserAdmin(UserAdmin[User]):
    readonly_fields = ("membership_type",)

    def get_membership_type(self, obj: User) -> MembershipYear | None:
        return obj.membership_type

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "license", "member_id")}),
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
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        ("Membership", {"fields": ("membership_type",)}),
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
