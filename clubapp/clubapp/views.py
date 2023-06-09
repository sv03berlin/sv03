from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")


@login_required
def settings(request: HttpRequest) -> HttpResponse:
    return render(request, "settings.html")
