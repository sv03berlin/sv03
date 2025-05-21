from io import BytesIO
from logging import getLogger
from typing import Any, cast, no_type_check

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import EmailMessage, send_mail
from django.db import models, transaction
from django.db.models import Q
from django.db.models.functions import ExtractYear
from django.db.models.query import QuerySet
from django.http import (
    FileResponse,
    HttpRequest,
    HttpResponse,
    HttpResponseNotAllowed,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django_filters import FilterSet, NumberFilter
from django_filters.views import FilterView
from openpyxl import Workbook

from clubapp.club.models import User
from clubapp.clubapp.decorators import is_ressort_user
from clubapp.clubapp.utils import AuthenticatedHttpRequest

from .forms import (
    ClubWorkForm,
    ClubWorkParticipationForm,
    ClubWorkPartitipationRessortUserCreatingForm,
    EmailUsersForm,
    HourEditForm,
)
from .models import ClubWork, ClubWorkParticipation

logger = getLogger(__name__)


def get_post_action(request: AuthenticatedHttpRequest) -> str:
    if request.method == "POST":
        return request.POST.get("post_action", "POST").lower()
    return ""


def is_delete_action(request: AuthenticatedHttpRequest) -> bool:
    return get_post_action(request) == "delete"


def is_post_action(request: AuthenticatedHttpRequest) -> bool:
    return get_post_action(request) == "post"


@login_required
def clubwork_index(request: AuthenticatedHttpRequest) -> HttpResponse:
    upcoming = [
        cw
        for cw in request.user.clubwork_participations.filter(
            date_time__gte=timezone.now(), is_approved=False
        ).order_by("date_time")
        if (cw.clubwork is not None)
    ]
    clubworks = [
        cw for cw in ClubWork.objects.filter(date_time__gte=timezone.now()).order_by("date_time") if not cw.is_full
    ]

    for cw in upcoming:
        if cw.clubwork is not None and cw.clubwork in clubworks:
            clubworks.remove(cw.clubwork)

    c = {
        "this_year": timezone.now().year,
        "user": request.user,
        "upcoming_clubwork_user": upcoming,
        "clubworks": clubworks,
    }
    return render(request, template_name="clubwork.html", context=c)


@login_required
@is_ressort_user
def add_clubwork(request: AuthenticatedHttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ClubWorkForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("clubwork_index")
        messages.error(request, str(form.errors))
    c = {"form": ClubWorkForm(), "heading": "Ausschreibung erstellen"}
    return render(request, template_name="create_form.html", context=c)


@is_ressort_user
def mod_clubwork(request: AuthenticatedHttpRequest, pk: int) -> HttpResponse:
    if is_post_action(request):
        form = ClubWorkForm(request.POST, instance=ClubWork.objects.get(pk=pk))
        if form.is_valid():
            form.save()
            for application in form.instance.participations.all():
                if not application.is_approved:
                    application.title = form.instance.title
                    application.description = form.instance.description
                    application.date_time = form.instance.date_time
                    application.duration = form.instance.max_duration
                    application.ressort = form.instance.ressort
                    application.save()
            return redirect("clubwork_history")
        messages.error(request, str(form.errors))
    elif is_delete_action(request):
        ClubWork.objects.get(pk=pk).delete()
        return redirect("clubwork_index")
    c = {"form": ClubWorkForm(instance=ClubWork.objects.get(pk=pk)), "heading": "Ausschreibung bearbeiten"}
    return render(request, template_name="create_form.html", context=c)


class IsRessortOrAdminMixin(UserPassesTestMixin):
    request: HttpRequest

    def test_func(self) -> bool:
        if not self.request.user.is_authenticated:
            return False
        user = self.request.user
        return user.is_superuser or user.is_ressort_user


class ClubWorkDelete(IsRessortOrAdminMixin, DeleteView):  # type: ignore[type-arg]
    template_name = "delete_form.html"
    queryset = ClubWork.objects.all()
    success_url = reverse_lazy("clubwork_index")

    def form_valid(self, form: Any) -> HttpResponse:  # noqa: ARG002
        success_url = self.get_success_url()
        try:
            self.object.delete()
        except models.ProtectedError:
            messages.error(
                self.request, "Dieser Arbeitsdienst kann nicht gelöscht werden, da es angemeldete Benutzer gibt."
            )
        return HttpResponseRedirect(success_url)


class OwnClubworkMixin:
    model = ClubWorkParticipation

    @no_type_check
    def get_queryset(self) -> QuerySet[ClubWorkParticipation]:
        if self.request.user.is_ressort_user or self.request.user.is_staff or self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(user=self.request.user, is_approved=False)

    def get_success_url(self) -> str:
        return reverse("clubwork_index")

    @no_type_check
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["heading"] = "Eigenen Arbeitsdienst anmelden"
        return c


class OwnClubWorkCreate(LoginRequiredMixin, OwnClubworkMixin, CreateView):  # type: ignore[type-arg]
    template_name = "create_form.html"
    form_class = ClubWorkParticipationForm

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class OwnClubWorkUpdate(LoginRequiredMixin, OwnClubworkMixin, UpdateView):  # type: ignore[type-arg]
    template_name = "create_form.html"
    form_class = ClubWorkParticipationForm

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["instance"] = self.get_object()
        return kwargs


class HourUpdateView(UpdateView[ClubWorkParticipation, HourEditForm]):
    model = ClubWorkParticipation
    form_class = HourEditForm
    template_name = "create_form.html"

    @no_type_check
    def get_queryset(self) -> QuerySet[ClubWorkParticipation]:
        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(user=self.request.user, is_approved=False)

    def get_success_url(self) -> str:
        return reverse("clubwork_user_history")

    @no_type_check
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["heading"] = "Arbeitsstunden Arbeitsdienst Eintragen"
        return c


class OwnClubWorkDelete(LoginRequiredMixin, OwnClubworkMixin, DeleteView):  # type: ignore[type-arg]
    template_name = "abmelden_delete_form.html"


@login_required
@is_ressort_user
def approve_clubwork_overview(request: AuthenticatedHttpRequest) -> HttpResponse:
    cw = ClubWorkParticipation.objects.filter(
        is_approved=False, ressort__head__in=[request.user.pk], date_time__lte=timezone.now()
    ).order_by("date_time")
    return render(request, template_name="approve_clubwork.html", context={"clubworks": cw})


@login_required
@is_ressort_user
def approve_clubwork(request: AuthenticatedHttpRequest, pk: int) -> HttpResponse:
    if request.method == "POST":
        part = ClubWorkParticipation.objects.get(pk=pk)
        if not part.is_approved:
            part.approved_by = request.user
            part.is_approved = True
            part.approve_date = timezone.now()
            part.save()
            part.notify_approval(request)
            return HttpResponse(status=204)
    if request.method == "DELETE":
        part = ClubWorkParticipation.objects.get(pk=pk)
        part.delete()
        return HttpResponse(status=204)
    return redirect("approve_clubwork")


@login_required
def register_for_clubwork(request: AuthenticatedHttpRequest, pk: int) -> HttpResponse:
    with transaction.atomic():
        cw = ClubWork.objects.get(pk=pk)
        if cw.is_full:
            messages.error(request, "Dieser Arbeitsdienst ist bereits voll.")
            return redirect("clubwork_index")

        if request.method == "POST":
            if cw.participations.filter(user=request.user).exists():
                messages.error(request, "Du bist bereits für diesen Arbeitsdienst angemeldet.")
                return redirect("clubwork_index")

            ClubWorkParticipation.objects.create(
                title=cw.title,
                user=request.user,
                ressort=cw.ressort,
                clubwork=cw,
                date_time=cw.date_time,
                duration=cw.max_duration,
                description=cw.description,
            )
        return redirect("clubwork_index")


@login_required
def unregister_for_clubwork(request: AuthenticatedHttpRequest, pk: int) -> HttpResponse:
    with transaction.atomic():
        cw = ClubWork.objects.get(pk=pk)
        if request.method == "POST":
            part = ClubWorkParticipation.objects.get(clubwork=cw, user=request.user)
            if not (
                request.user.is_staff
                or request.user.is_superuser
                or request.user.is_ressort_user
                or request.user == part.user
            ):
                messages.error(request, "Du kannst nur deine eigenen Anmeldungen löschen.")
                return redirect("clubwork_index")
            if not part.is_approved:
                part.delete()
            else:
                messages.error(request, "Du kannst nur nicht noch nicht genehmigte Anmeldungen löschen.")
        return redirect("clubwork_index")


@is_ressort_user
@login_required
def history(request: AuthenticatedHttpRequest) -> HttpResponse:
    c: dict[str, Any] = {}
    c["years"] = ["all"] + [str(x.year) for x in ClubWorkParticipation.objects.dates("date_time", "year")]
    c["selected_year"] = request.GET.get("year", "all")
    c["years"].remove(c["selected_year"])

    year_qs = ClubWorkParticipation.objects.filter(~Q(is_approved=False))
    if c["selected_year"] != "all":
        year_qs = year_qs.filter(date_time__year=c["selected_year"])
    c["clubworks"] = year_qs
    return render(request, template_name="clubwork_history.html", context=c)


class YearFilter(FilterSet):  # type: ignore[misc]
    year = NumberFilter(
        field_name="date_time",
        lookup_expr="year",
        label="Year",
        widget=forms.Select(choices=[]),
    )

    @property
    def choices(self) -> list[int]:
        return [
            item["year"]
            for item in ClubWorkParticipation.objects.annotate(year=ExtractYear("date_time"))
            .values("year")
            .distinct()
            .order_by("-year")
        ]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.filters["year"].field.widget.choices = self.get_year_choices()

        if self.data.get("year") == "":
            self.filters.pop("year")

    def get_year_choices(self) -> list[tuple[str, str]]:
        return [("", "all")] + [(str(x), str(x)) for x in self.choices]

    class Meta:
        model = ClubWorkParticipation
        fields = ["year"]


class HistoryFilter(YearFilter):
    class Meta(YearFilter.Meta):
        fields = [*YearFilter.Meta.fields, "ressort"]


class ClubworkHistoryView(LoginRequiredMixin, IsRessortOrAdminMixin, FilterView):  # type: ignore[misc]
    model = ClubWorkParticipation
    template_name = "clubwork_history.html"
    filterset_class = HistoryFilter

    def get_queryset(self) -> QuerySet[ClubWorkParticipation]:
        return super().get_queryset().filter()  # type: ignore[no-any-return]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        if "object_list" in kwargs:
            c.update({"clubworks": kwargs["object_list"]})
        return c  # type: ignore[no-any-return]

    def get(self, request: AuthenticatedHttpRequest, *args: Any, **kwargs: Any) -> HttpResponse | FileResponse | Any:
        if request.GET.get("xlsx", "false").lower() == "true":
            year = request.GET.get("year")
            if not year:
                messages.error(request, "Du musst ein Jahr auswählen um eine Excel Datei zu erstellen.")
                return super().get(request, *args, **kwargs)
            if year:
                return redirect(reverse("download", args=[year]))
            messages.error(request, "Du musst ein Jahr auswählen um eine Excel Datei zu erstellen.")
        return super().get(request, *args, **kwargs)


@login_required
@is_ressort_user
def download_xlsx_view(request: AuthenticatedHttpRequest, year: int) -> HttpResponse | FileResponse | Any:
    if ClubWorkParticipation.objects.filter(date_time__year=int(year), is_approved=False).exists():
        messages.error(request, f"Es existirern noch Arbeitsdienste mit ausstehenden Genehmigungen für {year}")
    else:
        messages.info(request, f"Alle Arbeitsdienste für {year} wurden Genehmigt")
    if request.GET.get("xlsx", "false").lower() == "true":
        if not year:
            messages.error(request, "Du musst ein Jahr auswählen um eine Excel Datei zu erstellen.")
        if year:
            r = FileResponse(
                get_xlsx(int(year)),
                status=200,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                as_attachment=True,
            )
            r["Content-Disposition"] = f"attachment; filename=arbeitsdienst_{year}.xlsx"
            return r
        messages.error(request, "Du musst ein Jahr auswählen um eine Excel Datei zu erstellen.")
    return render(request, "download.html", context={"year": year})


def get_xlsx(year: int) -> BytesIO:
    users = User.objects.filter(is_active=True).order_by("last_name")
    wb = Workbook()
    ws = wb.active
    ws.append(
        [
            "Name",
            "Vorname",
            "Email",
            "Mitgliedsnummer",
            "Altersbefreiung",
            "Mitgliedschaftstyp",
            "Stunden durch Mitgliedschaft",
            "Stunden Clubbootnutzer",
            "Stunden Bootseigner",
            "Stunden gleistet",
            "Stunden versäumt",
            "Stunden Gesamt",
            "Verrechnungssatz pro Stunde in Euro",
            "Ausbezahlt am Jahresanfang",
            "Kompensation in Euro",
        ]
    )
    for user in users:
        m = user.membership_type_year(year)
        if not m:
            continue
        be = m.work_hours_boat_owner if user.is_boat_owner else 0
        cb = m.work_hours_club_boat_user if user.is_clubboat_user else 0
        ws.append(
            [
                user.last_name,
                user.first_name,
                user.email,
                user.member_id,
                user.member_is_freed_from_work_by_age(year),
                m.name,
                m.work_hours,
                cb,
                be,
                user.hours_done_year(year),
                user.missing_hours(year),
                user.club_work_hours,
                m.work_compensation,
                m.full_work_compensation,
                user.club_work_compensation(year),
            ]
        )
    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)
    return bio


class UserHistroyView(LoginRequiredMixin, ListView[ClubWorkParticipation]):
    model = ClubWorkParticipation
    template_name = "clubwork_user_history.html"

    def get_queryset(self) -> QuerySet[ClubWorkParticipation]:
        user = cast(User, self.request.user)
        return super().get_queryset().filter(user=user)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c.update({"clubworks": self.get_queryset()})
        return c


class AllClubworkHistoryView(LoginRequiredMixin, IsRessortOrAdminMixin, FilterView):  # type: ignore[misc]
    model = ClubWork
    template_name = "clubwork_all.html"
    filterset_class = HistoryFilter

    def get_queryset(self) -> QuerySet[ClubWork]:
        return super().get_queryset()  # type: ignore[no-any-return]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        if "object_list" in kwargs:
            c.update({"clubworks": kwargs["object_list"]})
        return c  # type: ignore[no-any-return]

    def get(self, request: AuthenticatedHttpRequest, *args: Any, **kwargs: Any) -> HttpResponse | FileResponse | Any:
        if not request.user.is_ressort_user:
            return redirect("clubwork_index")

        return super().get(request, *args, **kwargs)


def notify_members_new_clubwork(users: list[User], request: AuthenticatedHttpRequest, clubwork: ClubWork) -> None:
    emails = [user.email for user in users]
    try:
        email = EmailMessage(
            subject=f"Arbeitsdienst {clubwork.title}",
            body=(
                f"Liebes Mitglied,\n\n"
                f"es ist ein neuer Arbeitsdienst verfügbar: {clubwork.title} am {clubwork.date_time}.\n"
                f"Beschreibung: {clubwork.description}\n\n"
                f"Du kannst dich hier anmelden: {settings.VIRTUAL_HOST}{reverse('clubwork_index')}\n\n"
                f"Viele Grüße,\n"
                f"{request.user.first_name} {request.user.last_name}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            bcc=emails,
        )
        email.send(fail_silently=False)
    except Exception:
        logger.exception("Error while sending email clubwork %s", clubwork.pk)
        messages.error(request, "Senden der email fehlgeschlagen")
        raise


@login_required
@is_ressort_user
def select_users_to_email_about(request: AuthenticatedHttpRequest, pk: int) -> HttpResponse:
    cw = get_object_or_404(ClubWork, pk=pk)
    if request.method == "POST":
        form = EmailUsersForm(request.POST)
        if form.is_valid():
            users: list[User] = form.cleaned_data["users"]
            notify_members_new_clubwork(users=users, clubwork=cw, request=request)
            return redirect("clubwork_index")
        messages.error(request, "Bitte wähle mindestens einen Nutzer aus.")
    else:
        form = EmailUsersForm()

    c = {
        "form": form,
        "clubwork": cw,
        "heading": f"Mitglieder über Clubdienst {cw} informieren",
        "action_text": "Email senden",
    }
    return render(request, template_name="create_form.html", context=c)


@login_required
@is_ressort_user
def email_all_users_clubwork(request: AuthenticatedHttpRequest, pk: int) -> HttpResponse:
    cw = get_object_or_404(ClubWork, pk=pk)
    if request.method == "GET":
        notify_members_new_clubwork(users=User.get_members(), clubwork=cw, request=request)
        return redirect("clubwork_index")
    msg = "GET"
    return HttpResponseNotAllowed(msg)


@login_required
@is_ressort_user
def register_user(request: AuthenticatedHttpRequest, pk: int) -> HttpResponse:
    cw = get_object_or_404(ClubWork, pk=pk)
    if request.method == "POST":
        form = EmailUsersForm(request.POST)
        if form.is_valid():
            users = form.cleaned_data["users"]
            for user in users:
                try:
                    ClubWorkParticipation.objects.get_or_create(
                        title=cw.title,
                        user=user,
                        ressort=cw.ressort,
                        clubwork=cw,
                        date_time=cw.date_time,
                        duration=cw.max_duration,
                        description=cw.description,
                    )
                    send_mail(
                        subject=f"Arbeitsdienst {cw.title}",
                        message=f"Hallo {user.first_name},\n\n"
                        f"du wurdest für {cw.title} am {cw.date_time} eingetragen\n"
                        f"Beschreibung: {cw.description}\n\n"
                        f"Du kannst dich hier abmelden: {settings.VIRTUAL_HOST}{reverse('clubwork_index')}\n\n"
                        f"Viele Grüße,\n"
                        f"{request.user.first_name} {request.user.last_name}",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                except Exception:
                    logger.exception("Error while sending email to user %s", user)
                    messages.error(
                        request, f"Der Nutzer mit der ID {user} existiert nicht oder wurde bereits ausgewählt."
                    )
            return redirect("clubwork_index")
    else:
        form = EmailUsersForm()

    c = {
        "form": form,
        "clubwork": cw,
        "heading": f"Mitglieder für Clubdienst {cw} anmelden",
        "action_text": "Anmelden",
    }
    return render(request, template_name="create_form.html", context=c)


@login_required
@is_ressort_user
def unregister_user_for_clubwork(request: AuthenticatedHttpRequest, clubwork_id: int, user_id: int) -> HttpResponse:
    with transaction.atomic():
        cw = ClubWork.objects.get(pk=clubwork_id)
        if request.method == "POST":
            part = ClubWorkParticipation.objects.get(clubwork=cw, user_id=user_id)
            if not part.is_approved:
                part.delete()
            else:
                messages.error(request, "Du kannst nur nicht noch nicht genehmigte Anmeldungen löschen.")
        return redirect("clubwork_index")


class OtherUserClubWorkCreationForm(LoginRequiredMixin, OwnClubworkMixin, CreateView):  # type: ignore[type-arg]
    template_name = "create_form.html"
    form_class = ClubWorkPartitipationRessortUserCreatingForm

    def get_form_kwargs(self) -> Any:
        return {**super().get_form_kwargs(), "request": self.request}
