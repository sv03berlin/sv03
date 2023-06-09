from typing import Any

from django import forms
from django.http import HttpRequest

from clubapp.club.models import User


class AuthenticatedHttpRequest(HttpRequest):
    user: User


class DateTimeInput(forms.DateTimeInput):
    input_type = "datetime-local"

    def __init__(self, attrs: dict[str, Any] | None = None, format: str = "%Y-%m-%dT%H:%M:%S") -> None:
        super().__init__(attrs)
        self.format = format or None
