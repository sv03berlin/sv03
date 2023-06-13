from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe

from clubapp.clubapp.utils import AuthenticatedHttpRequest

from .calendar import Calendar


def calendar_month(request: AuthenticatedHttpRequest) -> HttpResponse:
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
