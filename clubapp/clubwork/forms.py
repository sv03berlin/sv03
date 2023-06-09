from django import forms

from clubapp.clubapp.utils import DateTimeInput

from . import models


class ClubWorkForm(forms.ModelForm[models.ClubWork]):
    class Meta:
        model = models.ClubWork
        fields = [
            "title",
            "resort",
            "date_time",
            "max_duration",
            "max_participants",
            "description",
        ]
        widgets = {
            "date_time": DateTimeInput(),
        }


class ClubWorkParticipationForm(forms.ModelForm[models.ClubWorkParticipation]):
    class Meta:
        model = models.ClubWorkParticipation
        fields = [
            "title",
            "resort",
            "date_time",
            "duration",
            "description",
        ]
        widgets = {
            "date_time": DateTimeInput(),
        }
