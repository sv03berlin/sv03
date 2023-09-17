from django.urls import path

from . import views

urlpatterns = [
    path("sewobe_import/", views.sewobe_import, name="sewobe_import"),
]
