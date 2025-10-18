from typing import Any

from django import forms
from django.http import HttpRequest

from clubapp.club.models import User


class AuthenticatedHttpRequest(HttpRequest):
    user: User


class DateTimeInput(forms.DateTimeInput):
    input_type = "datetime-local"

    def __init__(self, attrs: dict[str, Any] | None = None, format: str = "%Y-%m-%dT%H:%M") -> None:  # noqa: A002
        super().__init__(attrs)
        self.format = format or None


class StrippedIntegerField(forms.IntegerField):
    def to_python(self, value: Any) -> Any:
        if isinstance(value, str):
            value = value.strip()
        return super().to_python(value)
