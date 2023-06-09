from django.apps import AppConfig


class AppConfig(AppConfig):  # type: ignore[no-redef] # pylint: disable=function-redefined
    default_auto_field = "django.db.models.BigAutoField"
    name = "clubapp.refundflow"
