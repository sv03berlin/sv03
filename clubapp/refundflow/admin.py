from django.contrib import admin

from clubapp.refundflow.models import Tracking, Transaction


class TrackingAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("user",)
    autocomplete_fields = ["user", "transaction"]
    search_fields = ["user", "transaction__reason"]


class TransactionAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("amount", "user", "date")
    autocomplete_fields = ["user", "approved_by"]
    search_fields = ["user", "approved_by"]


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Tracking, TrackingAdmin)
