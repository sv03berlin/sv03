from datetime import datetime
from typing import Any

from django.forms import ModelForm

from clubapp.club.models import User
from clubapp.clubapp.utils import DateTimeInput

from .models import ReservabelThing, Reservation


class ReservationForm(ModelForm):  # type: ignore[type-arg]
    class Meta:
        model = Reservation
        fields = ["thing", "start", "end"]

        widgets = {
            "start": DateTimeInput(),
            "end": DateTimeInput(),
        }

    def __init__(self, user: User, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["thing"].choices = [("", "Bitte auswählen")] + self.allowed_to_borrow()  # type: ignore[attr-defined]
        instance = kwargs.get("instance")
        if instance:
            self.fields["thing"].initial = instance.thing

    def save(self, commit: bool = True) -> Reservation:
        reservation = super().save(commit=False)
        reservation.user = self.user
        if commit:
            reservation.save()
        return super().save(commit)  # type: ignore[no-any-return]

    def allowed_to_borrow(self) -> list[tuple[int, str]]:
        if self.user.is_staff:
            qs = ReservabelThing.objects.all()
        else:
            qs = ReservabelThing.objects.filter(reservation_group__memberships__user=self.user)
        return [(thing.id, thing.name) for thing in qs]

    def is_valid(self) -> bool:
        valid = super().is_valid()
        if not valid:
            return False

        start_time = self.cleaned_data["start"]
        end_time = self.cleaned_data["end"]

        if start_time < datetime.now():
            self.add_error("start", "Startzeit muss in der Zukunft liegen.")
            return False

        if start_time >= end_time:
            self.add_error("start", "Startzeit muss vor Endzeit liegen.")
            return False

        thing = self.cleaned_data["thing"]

        qs = Reservation.objects.all().exclude(thing=thing)

        # Check for any overlapping reservations
        overlapping_reservations = qs.filter(thing=thing, start__lt=end_time, end__gt=start_time)

        # Check if new reservation falls within the duration of an existing reservation
        containing_reservations = qs.filter(thing=thing, start__lte=start_time, end__gte=end_time)

        # Check if the start time of the new reservation is within the duration of an existing reservation
        containing_start_time_reservations = qs.filter(thing=thing, start__lt=start_time, end__gt=start_time)

        # Check if the end time of the new reservation is within the duration of an existing reservation
        containing_end_time_reservations = qs.filter(thing=thing, start__lt=end_time, end__gt=end_time)

        if (
            overlapping_reservations.exists()
            or containing_reservations.exists()
            or containing_start_time_reservations.exists()
            or containing_end_time_reservations.exists()
        ):
            self.add_error("thing", f"{thing.name} ist in diesem Zeitraum bereits reserviert.")
            return False

        print("valid")
        return True
