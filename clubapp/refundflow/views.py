import csv
import os
from datetime import date, datetime
from decimal import Decimal
from io import BytesIO, StringIO
from json import loads
from os import path, remove
from typing import Any, Union
from zipfile import ZipFile

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import UploadedFile
from django.core.mail import send_mail
from django.db import transaction
from django.http import FileResponse, HttpRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from xhtml2pdf import pisa

from clubapp.club.models import Ressort
from clubapp.clubapp.decorators import is_accountant_user, is_invoice_user, is_ressort_user
from clubapp.clubapp.settings import EMAIL_HOST_PASSWORD, EMAIL_HOST_USER, MEDIA_ROOT
from clubapp.clubapp.utils import AuthenticatedHttpRequest
from clubapp.refundflow.models import Tracking, Transaction

from .forms import AddTracking, SubmitRefund


@login_required
def transaction_overview(request: AuthenticatedHttpRequest) -> HttpResponse:
    c = {}
    if request.method == "POST":
        response_dict = loads(request.body.decode("utf-8"))
        if "remove" in response_dict:
            try:
                transaction = Transaction.objects.get(id=response_dict["remove"])
            except Transaction.DoesNotExist:
                return HttpResponse("Not Found", status=404)

            if transaction.user == request.user and transaction.status in [
                Transaction.StatusChoice.RECEIVED,
                Transaction.StatusChoice.REJECTED,
            ]:
                tracking = Tracking.objects.filter(user=request.user, transaction=transaction)
                for t in tracking:
                    t.transaction = None
                    t.save()

                remove(path.join(MEDIA_ROOT, transaction.invoice_path.path))
                print("deleteing", path.join(MEDIA_ROOT, transaction.invoice_path.path))
                transaction.delete()
                return HttpResponse("OK", status=200)
            return HttpResponse("Forbidden", status=403)

    c["transactions"] = reversed(Transaction.objects.filter(user_id=request.user.id))
    return render(request, "transaction_overview.html", c)


def handle_uploaded_file(f: Union[UploadedFile, list[object]], max_size_mb: int) -> Union[BytesIO, None]:
    assert isinstance(f, UploadedFile)
    bio = BytesIO()
    for chunk in f.chunks():
        bio.write(chunk)
        if bio.tell() > max_size_mb * 1024 * 1024:
            return None
    return bio


@login_required
def add_refund(request: AuthenticatedHttpRequest) -> HttpResponse:
    c: dict[str, Any] = {}
    if request.method == "POST":
        form = SubmitRefund(request.POST, request.FILES)
        if form.is_valid():
            pdf = handle_uploaded_file(request.FILES["file"], 10)
            if pdf is None:
                c["messages"] = ["File size exceeds 10MB"]
                return render(request, "add_refund.html", c)

            reason = form.cleaned_data["reason"]
            amount = form.cleaned_data["amount"]
            ressort = form.cleaned_data["ressort"]
            annotation = form.cleaned_data["annotation"]

            with transaction.atomic():
                t = Transaction(
                    user=request.user,
                    date=str(date.today()),
                    reason=reason,
                    ressort=Ressort.objects.get(id=ressort),
                    amount=amount,
                    annotation=annotation,
                    status=Transaction.StatusChoice.RECEIVED,
                )
                t.save()
                t.invoice_path.save(content=pdf, name=f"{t.id}.pdf")
                t.save()

            send_mail_transaction_approve(request, t)

            return redirect("transaction_overview")
        c["messages"] = ["Invalid form"]

    c["ressorts"] = Ressort.objects.all()
    return render(request, "add_refund.html", c)


def send_mail_transaction_approve(request: HttpRequest, t: Transaction) -> None:
    if t.ressort.head:
        try:
            send_mail(
                subject="Neue Rechnung zur Genehmigung",
                message=f"""Es ist eine neue Rechnung für {t.ressort.name} von {t.user.first_name} zur Genehmigung eingetroffen.
                            Bitte melde dich im System an, um sie zu bearbeiten.""",
                from_email=EMAIL_HOST_USER,
                recipient_list=[t.ressort.head.email],
                fail_silently=False,
                auth_user=EMAIL_HOST_USER,
                auth_password=EMAIL_HOST_PASSWORD,
            )
        except Exception:  # pylint: disable=broad-except
            print("Error while sending mail")
            messages.error(request, "Error while sending mail")


@is_invoice_user
@login_required
def tracking_overview(request: AuthenticatedHttpRequest) -> HttpResponse:
    c = {}
    if request.method == "POST":
        tracking_json = loads(request.body.decode("utf-8"))
        if "remove" in tracking_json:
            specific_tracking = get_object_or_404(Tracking, id=tracking_json["remove"])
            if specific_tracking.user == request.user and specific_tracking.transaction is None:
                specific_tracking.delete()
                return HttpResponse("OK", status=200)
            return HttpResponse("Forbidden", status=403)

    c["lots"] = reversed(Tracking.objects.filter(user=request.user))
    return render(request, "tracking_overview.html", c)


@is_invoice_user
@login_required
def add_tracking(request: AuthenticatedHttpRequest) -> HttpResponse:
    c = {}

    if request.method == "POST":
        form = AddTracking(request.POST)
        if form.is_valid():
            t = Tracking(
                user=request.user,
                date=form.cleaned_data["date"],
                reason=form.cleaned_data["reason"],
                ressort=form.cleaned_data["ressort"],
                annotation=form.cleaned_data["annotation"],
            )
            if form.cleaned_data["is_hour"]:
                t.payment_type = "hour"
                t.hour_rate = form.cleaned_data["amount"]
                t.hour_count = form.cleaned_data["hour_count"]
                assert t.hour_rate is not None
                assert t.hour_count is not None
                t.amount = t.hour_count * t.hour_rate
            else:
                t.payment_type = "flat"
                t.hour_rate = None
                t.hour_count = None
                t.amount = form.cleaned_data["amount"]

            t.save()
            return redirect("tracking_overview")

    c["ressorts"] = Ressort.objects.all()
    return render(request, "add_tracking.html", c)


@login_required
def invoice_generate(request: AuthenticatedHttpRequest) -> HttpResponse:
    for for_ressort in Ressort.objects.filter(tracking__user=request.user, tracking__transaction=None).distinct():
        c: dict[str, Any] = {}
        c["lots"] = Tracking.objects.filter(user=request.user, transaction=None, ressort=for_ressort)
        c["total"] = sum(t.amount for t in c["lots"])

        now = datetime.now()
        c["date"] = now.strftime("%d.%m.%Y")

        invoice_html = render_to_string("invoice.html", c, request=request)

        pisa.showLogging()
        pdf = BytesIO()
        pisa_status = pisa.pisaDocument(StringIO(invoice_html), pdf)

        if pisa_status.err:
            messages.error(request, "Error while generating invoice")
            return redirect("tracking_overview")

        try:
            t = Transaction(user=request.user, amount=Decimal(c["total"]))
            t.reason = (
                "Trainingsabrechnung von "
                + c["lots"].order_by("date")[0].date.strftime("%d.%m.%Y")
                + " bis "
                + c["lots"].order_by("-date")[0].date.strftime("%d.%m.%Y")
            )
            t.date = str(date.today())
            t.ressort = for_ressort
            t.status = Transaction.StatusChoice.RECEIVED
            t.save()

            t.invoice_path.save(name=f"{t.id}.pdf", content=pdf)
            t.save()

            for lot in c["lots"]:
                lot.transaction = t
                lot.save()

            send_mail_transaction_approve(request, t)

        except Exception:  # pylint: disable=broad-except
            messages.error(request, "Error while Saving in Database")

    return redirect("tracking_overview")


@login_required
@is_accountant_user
def manage_payment(request: HttpRequest) -> HttpResponse:
    c = {}
    if request.method == "POST":
        payment_json = loads(request.body.decode("utf-8"))
        if "paid" in payment_json:
            try:
                transaction = Transaction.objects.get(id=payment_json["paid"])
            except Transaction.DoesNotExist:
                return HttpResponse("Not Found", status=404)

            transaction.status = Transaction.StatusChoice.TRANSFERRED
            transaction.save()

            try:
                send_mail(
                    subject="Deine Zahlung wurde überwiesen",
                    message=f"Deine Zahlung für {transaction.ressort.name} wurde als überwiesen markiert",
                    from_email=EMAIL_HOST_USER,
                    recipient_list=[transaction.user.email],
                    fail_silently=False,
                    auth_user=EMAIL_HOST_USER,
                    auth_password=EMAIL_HOST_PASSWORD,
                )
            except Exception:
                print("Error while sending mail")
                messages.error(request, "Error while sending mail")

            return HttpResponse("OK", status=200)
        return HttpResponse("Not Found", status=404)

    c["transactions"] = reversed(Transaction.objects.filter(status=Transaction.StatusChoice.APPROVED))
    return render(request, "manage_payment.html", c)


@is_ressort_user
@login_required
def history(request: AuthenticatedHttpRequest) -> HttpResponse:
    c: dict[str, Any] = {}
    c["years"] = ["all"] + [str(x.year) for x in Transaction.objects.dates("date", "year")]
    c["selected_year"] = request.GET.get("year", "all")
    c["years"].remove(c["selected_year"])

    year_qs = Transaction.objects.filter(status=Transaction.StatusChoice.TRANSFERRED)
    if c["selected_year"] != "all":
        year_qs = year_qs.filter(date__year=c["selected_year"])
    if request.user.is_accountant_user:
        c["transactions"] = reversed(year_qs)
    else:
        ressort_qs = Ressort.objects.filter(head=request.user)
        c["transactions"] = reversed(year_qs.filter(ressort__in=ressort_qs))

    return render(request, "history.html", c)


@is_ressort_user
@login_required
def download(request: AuthenticatedHttpRequest) -> Union[HttpResponse, HttpResponseNotFound]:
    kind = request.GET.get("download", "csv")

    qs = Transaction.objects.filter(status=Transaction.StatusChoice.TRANSFERRED)
    if (year := request.GET.get("year", "all")) != "all":
        qs = qs.filter(date__year=year)
    if not request.user.is_accountant_user:
        ressort_qs = Ressort.objects.filter(head=request.user)
        qs = qs.filter(ressort__in=ressort_qs)

    if kind == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="transactions.csv"'
        # use ;
        writer = csv.writer(response, delimiter=";")
        writer.writerow(
            ["Datum", "Ressort", "User", "Betrag", "Grund", "Status", "Buchungsnummer", "Dateiname", "genemigt von", "Bemerkung"]
        )
        for t in qs:
            approved_by = t.approved_by.username if t.approved_by else ""
            writer.writerow(
                [
                    t.date,
                    t.ressort.name,
                    t.user.username,
                    t.amount,
                    t.reason,
                    t.status,
                    t.pk,
                    t.invoice_path,
                    approved_by,
                    t.annotation,
                ]
            )
        return response
    if kind == "zip":
        print("zip")
        bio = BytesIO()
        with ZipFile(bio, "w") as zf:
            for t in qs:
                pth = path.join(MEDIA_ROOT, t.invoice_path.path)
                if os.path.exists(pth):
                    zf.write(pth, str(t.id) + ".pdf")
        bio.seek(0)
        response = HttpResponse(bio.read(), content_type="application/zip")
        response["Content-Disposition"] = "attachment; filename=transactions.zip"
        return response
    return HttpResponseNotFound("Not Found")


@login_required
def invoice(request: AuthenticatedHttpRequest, pdf: int) -> Union[HttpResponse, FileResponse, HttpResponseNotFound]:
    specific_invoice = get_object_or_404(Transaction, pk=pdf)

    if specific_invoice.user == request.user or request.user.is_accountant_user or specific_invoice.ressort.head == request.user:
        try:
            return FileResponse(
                open(path.join(MEDIA_ROOT, specific_invoice.invoice_path.path), "rb"),
                content_type="application/pdf",
            )

        except FileNotFoundError:
            return HttpResponseNotFound("File not found")

    return HttpResponse(status=403)


@is_ressort_user
@login_required
def approve_payment(request: AuthenticatedHttpRequest) -> HttpResponse:
    c = {}
    qs = Ressort.objects.filter(head=request.user).values_list("id")
    if request.method == "POST":
        response_dict = loads(request.body.decode("utf-8"))

        if "id" in response_dict and "isApproved" in response_dict:
            try:
                transaction = Transaction.objects.get(id=response_dict["id"])
            except Transaction.DoesNotExist:
                return HttpResponse("Not Found", status=404)

            if (transaction.ressort.id,) in list(qs):
                msg = ""
                if response_dict["isApproved"]:
                    transaction.status = Transaction.StatusChoice.APPROVED
                    transaction.approved_by = request.user
                else:
                    transaction.status = Transaction.StatusChoice.REJECTED
                    msg += f" Bitte kontaktiere {request.user.username} für weitere Informationen."

                transaction.save()

                msg = f"Deine Rechnung vom {transaction.date} wurde von {request.user.username} {transaction.get_status_display()}." + msg
                try:
                    send_mail(
                        subject=f"Abrechnung wurde {transaction.get_status_display()}",
                        message=msg,
                        from_email=EMAIL_HOST_USER,
                        recipient_list=[transaction.user.email],
                        fail_silently=False,
                        auth_user=EMAIL_HOST_USER,
                        auth_password=EMAIL_HOST_PASSWORD,
                    )
                except Exception:
                    print("Error while sending mail")
                    messages.error(request, "Error while sending mail")

                return HttpResponse("OK", status=200)
            return HttpResponse("Forbidden", status=403)

    c["transactions"] = Transaction.objects.filter(status=Transaction.StatusChoice.RECEIVED, ressort__in=qs)
    return render(request, "approve_payment.html", c)
