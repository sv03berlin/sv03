from django.contrib import admin
from django.urls import include, path

from clubapp.clubapp import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("settings/", views.settings, name="settings"),
    path("refundflow/", include("clubapp.refundflow.urls")),
    path("clubwork/", include("clubapp.clubwork.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
]
