from json import dumps
from typing import Any, cast, no_type_check

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.urls import reverse
from django.utils.safestring import SafeString
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django_filters import FilterSet, NumberFilter
from django_filters.views import FilterView

from clubapp.club.models import User

from .forms import ReservationForm
from .models import Reservation, ReservationGroup


class ReservationMixin:
    model = Reservation

    @no_type_check
    def get_queryset(self) -> QuerySet[Reservation]:
        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(user=self.request.user)

    @no_type_check
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["heading"] = "Reservierung erstellen"
        return c

    def get_success_url(self) -> str:
        return reverse("reservation_list")


class ReservationCreateView(LoginRequiredMixin, ReservationMixin, CreateView):  # type: ignore[type-arg, misc]
    template_name = "create_form.html"
    form_class = ReservationForm

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class ReservationUpdateView(LoginRequiredMixin, ReservationMixin, UpdateView):  # type: ignore[type-arg, misc]
    template_name = "create_form.html"
    form_class = ReservationForm

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["instance"] = self.get_object()
        return kwargs


class ReservationDeleteView(LoginRequiredMixin, ReservationMixin, DeleteView):  # type: ignore[type-arg, misc]
    template_name = "delete_form.html"


class ReservationsListView(LoginRequiredMixin, ListView[Reservation]):
    model = Reservation
    template_name = "reservation_list.html"

    def get_queryset(self) -> Any:
        user = cast(User, self.request.user)
        return Reservation.objects.filter(user=user).order_by("-start")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["user"] = self.request.user
        c["reservations"] = self.get_queryset()
        return c


class StaffReservationsListView(ReservationsListView):
    def get_queryset(self) -> Any:
        return Reservation.objects.all().order_by("start")


class DetailReservationView(LoginRequiredMixin, DetailView[Reservation]):
    model = Reservation
    template_name = "reservation_detail.html"

    def get_queryset(self) -> QuerySet[Any]:
        return Reservation.objects.all()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["user"] = self.request.user
        c["edit_allowed"] = (
            self.request.user.is_staff or self.request.user.is_superuser or self.request.user == self.get_object().user
        )
        return c


class ReservationGroupFilter(FilterSet):  # type: ignore[misc]
    group = NumberFilter(
        field_name="thing__reservation_group",
        widget=forms.Select(choices=[]),
        label="Gruppe",
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.filters["group"].field.widget.choices = self.get_group_choices()

    def get_group_choices(self) -> list[tuple[str, str]]:
        return [("", "all")] + [(str(x.id), str(x.name)) for x in ReservationGroup.objects.all()]

    class Meta:
        model = Reservation
        fields = ["group"]


class CalendarDetailView(LoginRequiredMixin, FilterView):  # type: ignore[misc]
    model = Reservation
    template_name = "newcal.html"
    filterset_class = ReservationGroupFilter
    permission_denied_message = "You are not allowed to see this calendar."

    def get_context_data(self, **kwargs: Any) -> Any:
        c = super().get_context_data(**kwargs)
        c["events"] = SafeString(
            dumps(
                [
                    {
                        "id": event.id,
                        "title": event.__str__(),
                        "start": event.start.isoformat(),
                        "end": event.end.isoformat(),
                        "url": reverse("reservation_group_detail", kwargs={"pk": event.id}),
                    }
                    for event in kwargs["object_list"]
                ]
            )
        )
        return c
