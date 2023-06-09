from django.contrib import admin

from clubapp.refundflow.models import Tracking, Transaction

admin.site.register(Transaction)
admin.site.register(Tracking)
