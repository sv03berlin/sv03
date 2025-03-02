import calendar
import datetime
from typing import Any

from bootstrap_datepicker_plus.widgets import DatePickerInput, DateTimePickerInput, TimePickerInput
from django import forms
from django.db import transaction
from django.forms import ModelForm
from django.utils import timezone

from clubapp.club.models import User

from .models import ReservableThing, Reservation


def allowed_to_borrow(user: User) -> list[tuple[int, str]]:
    if user.is_superuser or user.is_ressort_user:
        qs = ReservableThing.objects.all()
    else:
        qs = ReservableThing.objects.filter(reservation_group__users__in=[user])
        qs |= ReservableThing.objects.filter(all_can_reserve=True)
        qs = qs.distinct().order_by("reservation_group")
    return [(thing.id, thing.name) for thing in qs]


def is_valid(
    form: "ReservationForm | SerialReservationForm",
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    thing: ReservableThing,
    qs: Any,
) -> bool:
    # Check for any overlapping reservations
    overlapping_reservations = qs.filter(start__lt=end_time, end__gt=start_time)

    # Check if new reservation falls within the duration of an existing reservation
    containing_reservations = qs.filter(start__lte=start_time, end__gte=end_time)

    # Check if the start time of the new reservation is within the duration of an existing reservation
    containing_start_time_reservations = qs.filter(start__lt=start_time, end__gt=start_time)

    # Check if the end time of the new reservation is within the duration of an existing reservation
    containing_end_time_reservations = qs.filter(start__lt=end_time, end__gt=end_time)

    if (
        overlapping_reservations.exists()
        or containing_reservations.exists()
        or containing_start_time_reservations.exists()
        or containing_end_time_reservations.exists()
    ):
        form.add_error("thing", f"{thing.name} ist in diesem Zeitraum bereits reserviert.")
        return False

    return True


class ReservationForm(ModelForm):  # type: ignore[type-arg]
    class Meta:
        model = Reservation
        fields = ["thing", "start", "end"]

        widgets = {
            "start": DateTimePickerInput(),
            "end": DateTimePickerInput(range_from="start"),
        }

    def __init__(self, user: User, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["thing"].choices = [("", "Bitte auswählen")] + allowed_to_borrow(user)  # type: ignore[attr-defined]
        instance = kwargs.get("instance")
        if instance:
            self.fields["thing"].initial = instance.thing

    def save(self, commit: bool = True) -> Reservation:
        reservation = super().save(commit=False)
        reservation.user = self.user
        if commit:
            reservation.save()
        return super().save(commit)  # type: ignore[no-any-return]

    def is_valid(self) -> bool:
        valid = super().is_valid()
        if not valid:
            return False

        start_time = self.cleaned_data["start"]
        end_time = self.cleaned_data["end"]
        thing = self.cleaned_data["thing"]

        if start_time < timezone.now() and self.instance.pk is None:
            self.add_error("start", "Startzeit muss in der Zukunft liegen.")
            return False

        if start_time >= end_time:
            self.add_error("start", "Startzeit muss vor Endzeit liegen.")
            return False

        return is_valid(
            self, start_time, end_time, thing, Reservation.objects.filter(thing=thing).exclude(id=self.instance.id)
        )


class SerialReservationForm(forms.Form):
    WEEKDAYS = [(str(i), calendar.day_name[i]) for i in range(7)]

    things = forms.MultipleChoiceField(choices=[], required=True, widget=forms.CheckboxSelectMultiple, label="Objekt")

    multiselect_weekdays = forms.MultipleChoiceField(
        choices=WEEKDAYS, widget=forms.CheckboxSelectMultiple, label="Wochentage"
    )
    first_day = forms.DateField(
        widget=DatePickerInput(), label="Erster Tag", initial=datetime.datetime.now(tz=datetime.UTC)
    )
    last_day = forms.DateField(
        widget=DatePickerInput(), label="Letzter Tag", initial=datetime.datetime.now(tz=datetime.UTC)
    )
    starttime = forms.TimeField(
        widget=TimePickerInput(), label="Startzeit", initial=datetime.datetime.now(tz=datetime.UTC)
    )
    endtime = forms.TimeField(widget=TimePickerInput(), label="Endzeit", initial=datetime.datetime.now(tz=datetime.UTC))

    class Meta:
        fields = ["multiselect_weekdays", "first_day", "last_day", "start_time", "end_time"]

        widgets = {
            "first_day": DatePickerInput(),
            "last_day": DatePickerInput(),
            "start_time": TimePickerInput(),
            "end_time": TimePickerInput(),
        }

    def __init__(self, user: User, *args: Any, **kwargs: Any) -> None:
        kwargs.pop("instance")
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["things"].choices = allowed_to_borrow(user)  # type: ignore[attr-defined]

    def is_valid(self) -> bool:
        valid = super().is_valid()
        if not valid:
            return False
        return all(
            is_valid(self, r.start, r.end, r.thing, Reservation.objects.filter(thing=r.thing))
            for r in self.reservations
        )

    @transaction.atomic
    def save(self) -> None:
        for r in self.reservations:
            r.save()

    @property
    def reservations(self) -> list[Reservation]:
        reservations = []
        weekdays = [int(day) for day in self.cleaned_data["multiselect_weekdays"]]
        first_day = self.cleaned_data["first_day"]
        last_day = self.cleaned_data["last_day"]
        starttime = self.cleaned_data["starttime"]
        endtime = self.cleaned_data["endtime"]
        user = self.user
        things = ReservableThing.objects.filter(pk__in=[int(o) for o in self.cleaned_data["things"]])

        for thing in things:
            current_date = first_day
            while current_date <= last_day:
                if current_date.weekday() in weekdays:
                    start_datetime = datetime.datetime.combine(current_date, starttime)
                    end_datetime = datetime.datetime.combine(current_date, endtime)
                    reservation = Reservation(
                        thing=thing,
                        start=start_datetime,
                        end=end_datetime,
                        user=user,
                    )
                    reservations.append(reservation)
                current_date += datetime.timedelta(days=1)
        return reservations
