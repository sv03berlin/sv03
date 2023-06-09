from django.urls import path

from . import views

urlpatterns = [
    path("managepayment/", views.manage_payment, name="manage_payment"),
    path("transactionhistory/", views.history, name="history"),
    path("invoice/<int:pdf>/", views.invoice, name="invoice"),
    path("approvepayment/", views.approve_payment, name="approve_payment"),
    path("transactionoverview/", views.transaction_overview, name="transaction_overview"),
    path("download/", views.download, name="download"),
    path("add_refund/", views.add_refund, name="add_refund"),
    path("trackingoverview/", views.tracking_overview, name="tracking_overview"),
    path("add_tracking/", views.add_tracking, name="add_tracking"),
    path("invoice_generate/", views.invoice_generate, name="invoice_generate"),
]
