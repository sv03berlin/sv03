from django.contrib import admin

from .models import ReservabelThing, Reservation, ReservationGroup


class ReservationsAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    model = Reservation
    autocomplete_fields = ["user", "thing"]
    search_fields = ["user", "thing"]


class ReservabelThingAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    model = ReservabelThing
    search_fields = ["name"]

class ReservationGroupAdmin(admin.ModelAdmin):
    model = ReservationGroup
    filter_horizontal = ["users"] 


admin.site.register(ReservationGroup, ReservationGroupAdmin)
admin.site.register(ReservabelThing, ReservabelThingAdmin)
admin.site.register(Reservation, ReservationsAdmin)
