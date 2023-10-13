from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from clubapp.clubapp import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("settings/", views.user_settings, name="settings"),
    path("refundflow/", include("clubapp.refundflow.urls")),
    path("clubwork/", include("clubapp.clubwork.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("reservations/", include("clubapp.reservationflow.urls")),
]

if settings.ENABLE_OIDC_LOGIN:
    urlpatterns.append(path("oidc/", include("mozilla_django_oidc.urls")))
