from django.contrib import admin

from .models import ReservableThing, Reservation, ReservationGroup


class ReservationsAdmin(admin.ModelAdmin[Reservation]):
    model = Reservation
    autocomplete_fields = ["user", "thing"]
    search_fields = ["user", "thing"]


class ReservableThingAdmin(admin.ModelAdmin[ReservableThing]):
    model = ReservableThing
    search_fields = ["name"]


# make users not required
class ReservationGroupAdmin(admin.ModelAdmin[ReservationGroup]):
    model = ReservationGroup
    filter_horizontal = ["users"]


admin.site.register(ReservationGroup, ReservationGroupAdmin)
admin.site.register(ReservableThing, ReservableThingAdmin)
admin.site.register(Reservation, ReservationsAdmin)
