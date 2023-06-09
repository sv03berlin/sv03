from datetime import datetime
from typing import Any

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render

from clubapp.clubapp.decorators import is_resort_user
from clubapp.clubapp.utils import AuthenticatedHttpRequest

from .forms import ClubWorkForm, ClubWorkParticipationForm
from .models import ClubWork, ClubWorkParticipation


@login_required
def clubwork_index(request: AuthenticatedHttpRequest) -> HttpResponse:
    c = {
        "this_year": datetime.now().year,
        "user": request.user,
        "upcoming_clubwork_user": request.user.clubwork_participations.filter(date_time__gte=datetime.now(), approved_by=None).order_by(
            "date_time"
        ),
        "clubworks": ClubWork.objects.filter(date_time__gte=datetime.now()).order_by("date_time"),
    }
    return render(request, template_name="clubwork.html", context=c)


@login_required
@staff_member_required
def add_clubwork(request: AuthenticatedHttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ClubWorkForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("clubwork_index")
        else:
            messages.error(request, str(form.errors))
    c = {"form": ClubWorkForm(), "heading": "Ausschreibung erstellen"}
    return render(request, template_name="create_form.html", context=c)


@login_required
def mod_clubwork(request: AuthenticatedHttpRequest, pk: int) -> HttpResponse:
    if request.method == "POST":
        form = ClubWorkForm(request.POST, instance=ClubWork.objects.get(pk=pk))
        if form.is_valid():
            form.save()
            return redirect("clubwork_index")
        else:
            messages.error(request, str(form.errors))
    elif request.method == "DELETE":
        ClubWork.objects.get(pk=pk).delete()
        return redirect("clubwork_index")
    c = {"form": ClubWorkForm(instance=ClubWork.objects.get(pk=pk)), "heading": "Ausschreibung bearbeiten"}
    return render(request, template_name="create_form.html", context=c)


@login_required
def add_own_clubwork(request: AuthenticatedHttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ClubWorkParticipationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("clubwork_index")
        else:
            messages.error(request, str(form.errors))
    c = {"form": ClubWorkParticipationForm(), "heading": "Eigenen Clubdienst anmelden"}
    return render(request, template_name="create_form.html", context=c)


@login_required
def mod_own_clubwork(request: AuthenticatedHttpRequest, pk: int) -> HttpResponse:
    cw = ClubWorkParticipation.objects.get(pk=pk)
    if cw.approved_by is not None and cw.approved_by != request.user:
        messages.error(request, "Du kannst nur deine eigenen Anmeldungen bearbeiten.")
        return redirect("clubwork_index")
    if request.method == "POST":
        form = ClubWorkParticipationForm(request.POST, instance=cw)
        if form.is_valid():
            form.save()
            return redirect("clubwork_index")
        else:
            messages.error(request, str(form.errors))
    elif request.method == "DELETE":
        ClubWorkParticipation.objects.get(pk=pk).delete()
        return HttpResponse(status=204)
    c = {
        "form": ClubWorkParticipationForm(instance=ClubWorkParticipation.objects.get(pk=pk)),
        "heading": "Eigenen Clubdienst bearbeiten",
    }
    return render(request, template_name="create_form.html", context=c)


@login_required
@is_resort_user
def approve_clubwork_overview(request: AuthenticatedHttpRequest) -> HttpResponse:
    cw = ClubWorkParticipation.objects.filter(approved_by=None, resort__head=request.user)
    return render(request, template_name="approve_clubwork.html", context={"clubworks": cw})


@login_required
@is_resort_user
def approve_clubwork(request: AuthenticatedHttpRequest, pk: int) -> HttpResponse:
    if request.method == "POST":
        part = ClubWorkParticipation.objects.get(pk=pk)
        if part.approved_by is None:
            part.approved_by = request.user
            part.approve_date = datetime.now()
            part.save()
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
        if cw.num_participants >= cw.max_participants:
            messages.error(request, "Dieser Arbeitsdienst ist bereits voll.")
            return render(request, "clubwork_index")

        if request.method == "POST":
            if cw.participations.filter(user=request.user).exists():
                messages.error(request, "Du bist bereits für diesen Arbeitsdienst angemeldet.")
                return redirect("clubwork_index")

            ClubWorkParticipation.objects.create(
                title=cw.title,
                user=request.user,
                resort=cw.resort,
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
            if not request.user.is_staff or request.user != part.user:
                messages.error(request, "Du kannst nur deine eigenen Anmeldungen löschen.")
                return redirect("clubwork_index")
            if part.approved_by is None:
                part.delete()
            else:
                messages.error(request, "Du kannst nur nicht noch nicht genehmigte Anmeldungen löschen.")
        return redirect("clubwork_index")


@is_resort_user
@login_required
def history(request: AuthenticatedHttpRequest) -> HttpResponse:
    c: dict[str, Any] = {}
    c["years"] = ["all"] + [str(x.year) for x in ClubWorkParticipation.objects.dates("date_time", "year")]
    c["selected_year"] = request.GET.get("year", "all")
    c["years"].remove(c["selected_year"])

    year_qs = ClubWorkParticipation.objects.filter(~Q(approved_by=None))
    if c["selected_year"] != "all":
        year_qs = year_qs.filter(date__year=c["selected_year"])
    c["clubworks"] = year_qs
    return render(request, template_name="clubwork_history.html", context=c)


@login_required
def user_history(request: AuthenticatedHttpRequest) -> HttpResponse:
    qs = ClubWorkParticipation.objects.filter(~Q(approved_by=None), user=request.user)
    c = {"clubworks": qs}
    return render(request, template_name="clubwork_user_history.html", context=c)
