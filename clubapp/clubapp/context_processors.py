import os
from typing import Any

from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from django.http import HttpRequest

from clubapp.club.models import User


def get_admins() -> list[User]:
    if (cached_admins := cache.get("admins")) is None:
        admins = list(User.objects.filter(Q(is_staff=True) | Q(is_superuser=True)))
        cache.set("admins", admins, 600)
        return admins
    return cached_admins  # type: ignore[no-any-return]


def club_processor(request: HttpRequest) -> dict[str, Any]:  # noqa: ARG001
    return {
        "staging": settings.STAGING,
        "club_name": settings.CLUB_NAME,
        "club_name_short": settings.CLUB_NAME_SHORT,
        "app_name": settings.THIS_APP_NAME,
        "club_imprint": settings.CLUB_IMPRINT,
        "enable_oidc_login": settings.ENABLE_OIDC_LOGIN,
        "enable_django_login": settings.ENABLE_DJANGO_LOGIN,
        "staff": get_admins(),
        "git_sha": os.environ.get("GIT_SHA"),
        "git_branch": os.environ.get("GIT_BRANCH"),
    }
