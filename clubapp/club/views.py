from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .importer import import_sewobe_xml


@staff_member_required
def sewobe_import(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        uploaded_file = request.FILES["file"]
        msgs = import_sewobe_xml(uploaded_file)
        for msg in msgs:
            messages.info(request, msg)

    return render(request, "sewobe_importer.html")
