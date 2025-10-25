"""
notes.views
===========

Views voor notities (lijst, detail, aanmaken, API, ...).
Bevat ook tag-weergave.
"""

from typing import List

from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Prefetch
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse

from .forms import NoteForm
from .models import Note, Tag


def list_notes(request: HttpRequest) -> HttpResponse:
    """
    Toon een lijst met notities met hun tags (prefetch om queries te beperken).
    """
    notes = Note.objects.all().prefetch_related(
        Prefetch("tags", queryset=Tag.objects.order_by("name"))
    )
    return render(request, "notes/list.html", {"notes": notes})


def create_note(request: HttpRequest) -> HttpResponse:
    """
    Maak een nieuwe notitie aan via een ModelForm.
    """
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Notitie is toegevoegd.")
            return redirect("notes:list")
    else:
        form = NoteForm()
    return render(request, "notes/form.html", {"form": form})


def detail_note(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Detailpagina voor één notitie.
    """
    note = get_object_or_404(Note.objects.prefetch_related("tags"), pk=pk)
    return render(request, "notes/detail.html", {"note": note})


def api_list_notes(request: HttpRequest) -> JsonResponse:
    """
    JSON-endpoint met id, title, created_at en tags per note.
    """
    qs = Note.objects.all().prefetch_related("tags")
    data: List[dict] = [
        {
            "id": n.id,
            "title": n.title,
            "created_at": n.created_at.isoformat() if n.created_at else None,
            "tags": [t.name for t in n.tags.all()],
        }
        for n in qs
    ]
    return JsonResponse(data, safe=False)
