from typing import Any

from django.conf import settings
from django.http import HttpRequest
from clubapp.club.models import User
from django.db.models import Q
from django.core.cache import cache


def get_admins() -> list[User]:
    if (cached_admins := cache.get("admins")) is None:
        admins = list(User.objects.filter(Q(is_staff=True) | Q(is_superuser=True)))
        cache.set("admins", admins, 600)
        return admins # type: ignore[no-any-return]
    else:
        return cached_admins


def club_processor(request: HttpRequest) -> dict[str, Any]:
    return {
        "staging": settings.STAGING,
        "club_name": settings.CLUB_NAME,
        "club_name_short": settings.CLUB_NAME_SHORT,
        "app_name": settings.THIS_APP_NAME,
        "club_imprint": settings.CLUB_IMPRINT,
        "enable_oidc_login": settings.ENABLE_OIDC_LOGIN,
        "enable_django_login": settings.ENABLE_DJANGO_LOGIN,
        "staff": get_admins(),
    }
