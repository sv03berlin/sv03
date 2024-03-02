from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def index(request: HttpRequest) -> HttpResponse:
    if settings.INDEX_IS_LOGIN and request.user.is_anonymous:
        return render(request, "registration/login.html")
    return render(request, "index.html")


@login_required
def user_settings(request: HttpRequest) -> HttpResponse:
    return render(request, "settings.html")
