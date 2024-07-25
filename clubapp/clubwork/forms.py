from typing import Any

from bootstrap_datepicker_plus.widgets import DateTimePickerInput
from django import forms

from clubapp.club.models import User

from . import models


class ClubWorkForm(forms.ModelForm[models.ClubWork]):
    class Meta:
        model = models.ClubWork
        fields = [
            "title",
            "ressort",
            "date_time",
            "async_date",
            "max_duration",
            "max_participants",
            "description",
        ]
        widgets = {
            "date_time": DateTimePickerInput(),
        }


class ClubWorkParticipationForm(forms.ModelForm[models.ClubWorkParticipation]):
    class Meta:
        model = models.ClubWorkParticipation
        fields = [
            "title",
            "ressort",
            "date_time",
            "duration",
            "description",
        ]
        widgets = {
            "date_time": DateTimePickerInput(),
        }

    def __init__(self, user: User, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.user = user

    def form_valid(self, form: forms.ModelForm[models.ClubWorkParticipation]) -> bool:
        form.instance.user = self.user
        return super().form_valid(form)  # type: ignore[no-any-return, misc]

    def save(self, commit: bool = True) -> models.ClubWorkParticipation:
        reservation = super().save(commit=False)
        reservation.user = self.user
        if commit:
            reservation.save()
        return super().save(commit)
