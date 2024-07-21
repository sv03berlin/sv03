from typing import cast

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from clubapp.club.models import User


def index(request: HttpRequest) -> HttpResponse:
    if settings.INDEX_IS_LOGIN and request.user.is_anonymous:
        return render(request, "registration/login.html")
    return render(request, "index.html")


@login_required
def user_settings(request: HttpRequest) -> HttpResponse:
    return render(request, "settings.html")


@login_required
def profile_overview(request: HttpRequest) -> HttpResponse:
    return render(request, "profile_overview.html", context={"user": request.user})


@login_required
def send_test_mail(request: HttpRequest) -> HttpResponse:
    user = cast(User, request.user)
    send_mail(
        subject="Sv03 Clubapp Test Email",
        message="This is a Test to check if email credentials are working.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    return HttpResponse(status=204)
