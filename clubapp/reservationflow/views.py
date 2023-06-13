from datetime import datetime
from typing import Any, cast, no_type_check

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from clubapp.club.models import User

from .calendar import Calendar
from .forms import ReservationForm
from .models import Reservation


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
        return Reservation.objects.filter(user=user).order_by("start")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["user"] = self.request.user
        c["reservations"] = self.get_queryset()
        return c


class StaffReservationsListView(ReservationsListView):
    def get_queryset(self) -> Any:
        return Reservation.objects.all().order_by("start")


class CalendarDetailView(LoginRequiredMixin, DetailView[Reservation]):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        year: int | str = request.GET.get("year", "")
        month: int | str = request.GET.get("month", "")
        if not year:
            year = datetime.now().year
        else:
            year = int(year)
        if not month:
            month = datetime.now().month
        else:
            month = int(month)
        cal = Calendar(year, month)
        html_cal = cal.formatmonth()
        c = {"cal": mark_safe(html_cal)}
        return render(request, "calendar.html", context=c)
