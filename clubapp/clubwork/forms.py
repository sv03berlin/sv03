from logging import getLogger
from typing import Any, cast

from bootstrap_datepicker_plus.widgets import DateTimePickerInput
from dal import autocomplete
from django import forms
from django.db.transaction import atomic

from clubapp.club.models import Ressort, User
from clubapp.clubapp.utils import AuthenticatedHttpRequest, StrippedIntegerField

from . import models

logger = getLogger()


class ClubWorkForm(forms.ModelForm[models.ClubWork]):
    max_duration = StrippedIntegerField()
    max_participants = StrippedIntegerField()

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
    duration = StrippedIntegerField()
    is_creating: bool

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
        self.is_creating = self.instance.pk is None

    def form_valid(self, form: forms.ModelForm[models.ClubWorkParticipation]) -> bool:
        if self.is_creating:
            form.instance.user = self.user
        return super().form_valid(form)  # type: ignore[no-any-return, misc]

    def save(self, commit: bool = True) -> models.ClubWorkParticipation:
        reservation = super().save(commit=False)
        if self.is_creating:
            reservation.user = self.user
        if commit:
            reservation.save()
        return super().save(commit)


class HourEditForm(forms.ModelForm[models.ClubWorkParticipation]):
    duration = StrippedIntegerField()

    class Meta:
        model = models.ClubWorkParticipation
        fields = [
            "duration",
            "description",
        ]


class ClubWorkPartitipationRessortUserCreatingForm(forms.ModelForm[models.ClubWorkParticipation]):
    duration = StrippedIntegerField()

    class Meta:
        model = models.ClubWorkParticipation
        fields = [
            "title",
            "users",
            "ressort",
            "date_time",
            "duration",
            "description",
        ]
        widgets = {"date_time": DateTimePickerInput()}

    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(), label="Mitglieder", required=True, widget=autocomplete.ModelSelect2Multiple()
    )
    request: AuthenticatedHttpRequest

    def __init__(self, request: AuthenticatedHttpRequest, *args: Any, **kwargs: Any) -> None:
        self.request = request
        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        if cleaned_data is None:
            raise ValueError
        ressort = cast("Ressort", cleaned_data.get("ressort"))

        if ressort and not (self.request.user.is_superuser or ressort.check_user_is_head(self.request.user)):
            msg = "You do not have permission to create a club work participation for this ressort."
            raise forms.ValidationError(msg)

        return cleaned_data

    @atomic
    def save(self, commit: bool = True) -> models.ClubWorkParticipation:
        instance = super().save(commit=False)
        users = self.cleaned_data["users"]
        if commit:
            for user in users:
                participation = models.ClubWorkParticipation(
                    title=instance.title,
                    ressort=instance.ressort,
                    date_time=instance.date_time,
                    duration=instance.duration,
                    description=instance.description,
                    user=user,
                    is_approved=True,
                    approved_by=self.request.user,
                )
                participation.save()
                participation.notify_approval(self.request)
        return instance


class EmailUsersForm(forms.Form):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(), label="Mitglieder", required=True, widget=autocomplete.ModelSelect2Multiple()
    )
