from typing import cast

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from clubapp.club.models import Ressort, User


def index(request: HttpRequest) -> HttpResponse:
    if settings.INDEX_IS_LOGIN and request.user.is_anonymous:
        return render(request, "registration/login.html")
    return render(request, "index.html", {"ressorts": Ressort.objects.all()})


@login_required
def user_settings(request: HttpRequest) -> HttpResponse:
    return render(request, "settings.html")


@login_required
def profile_overview(request: HttpRequest) -> HttpResponse:
    return render(request, "profile_overview.html", context={"user": request.user})


@login_required
def send_test_mail(request: HttpRequest) -> HttpResponse:
    user = cast("User", request.user)
    send_mail(
        subject="Sv03 Clubapp Test Email",
        message="This is a Test to check if email credentials are working.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    return HttpResponse(status=204)


def health(_: HttpRequest) -> HttpResponse:
    return JsonResponse({"status": "ok"}, status=200)


SECURITY = """Contact: mailto:webmaster@sv03.de
Expires: 2028-01-25T23:59:00.000Z
Preferred-Languages: de, en
"""


def security_txt(_request: HttpRequest) -> HttpResponse:
    return HttpResponse(SECURITY, content_type="text/plain")


ROBOTS = """User-agent: *
Disallow: /
"""


def robots_txt(_request: HttpRequest) -> HttpResponse:
    return HttpResponse(ROBOTS, content_type="text/plain")
