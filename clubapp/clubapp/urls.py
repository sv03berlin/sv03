from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path

from clubapp.clubapp import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("settings/", views.user_settings, name="settings"),
    path("health/", views.health, name="settings"),
    path("refundflow/", include("clubapp.refundflow.urls")),
    path("clubwork/", include("clubapp.clubwork.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("reservations/", include("clubapp.reservationflow.urls")),
    path("profile_overview/", views.profile_overview, name="profile_overview"),
    path("testmail/", views.send_test_mail, name="testmail"),
    re_path(r"^.well-known/security\.txt", views.security_txt),
    re_path(r"^security\.txt", views.security_txt),
    re_path(r"^robots\.txt", views.robots_txt),
]

if settings.ENABLE_OIDC_LOGIN:
    from clubapp.clubapp.oidc import provider_account_settings

    urlpatterns.append(path("oidc/", include("mozilla_django_oidc.urls")))
    urlpatterns.append(path("oidc/account/", provider_account_settings, name="oidc_account"))
