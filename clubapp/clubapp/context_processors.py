from typing import Any

from django.conf import settings
from django.http import HttpRequest


def club_processor(request: HttpRequest) -> dict[str, Any]:
    return {
        "staging": settings.STAGING,
        "club_name": settings.CLUB_NAME,
        "club_name_short": settings.CLUB_NAME_SHORT,
        "app_name": settings.THIS_APP_NAME,
        "club_imprint": settings.CLUB_IMPRINT,
    }
