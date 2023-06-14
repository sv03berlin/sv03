from django.contrib import admin

from .models import ReservabelThing, Reservation, ReservationGroup, ReservationGroupMembership


class ReservationGroupMembershipInline(admin.ModelAdmin):  # type: ignore[type-arg]
    model = ReservationGroupMembership
    autocomplete_fields = ["user"]


class ReservationsAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    model = Reservation
    autocomplete_fields = ["user", "thing"]
    search_fields = ["user", "thing"]


class ReservabelThingAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    model = ReservabelThing
    search_fields = ["name"]


admin.site.register(ReservationGroup)
admin.site.register(ReservabelThing, ReservabelThingAdmin)
admin.site.register(ReservationGroupMembership, ReservationGroupMembershipInline)
admin.site.register(Reservation, ReservationsAdmin)
