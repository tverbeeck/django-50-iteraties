"""
notes.views
===========

Views voor notities (lijst, detail, aanmaken, API, ...).
Bevat ook tag-weergave.
"""

import json

from typing import List

from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Prefetch, Q
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import (
    HttpRequest,
    HttpResponse,
    JsonResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
)

from .forms import NoteForm
from .models import Note, Tag


# let op: voeg Q toe bij je imports bovenin het bestand als dat er nog niet stond


def edit_note(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Bewerk een bestaande Note.
    - GET: toon formulier vooraf ingevuld
    - POST: valideer en sla op
    """
    note = get_object_or_404(Note, pk=pk)

    if request.method == "POST":
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, "Notitie is bijgewerkt.")
            return redirect("notes:detail", pk=note.pk)
    else:
        form = NoteForm(instance=note)

    return render(
        request,
        "notes/edit.html",
        {
            "form": form,
            "note": note,
        },
    )


def delete_note(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Verwijder een bestaande Note.
    - GET: toon confirm-schermpje
    - POST: voer de delete uit en redirect naar lijst
    """
    note = get_object_or_404(Note, pk=pk)

    if request.method == "POST":
        title = note.title
        note.delete()
        messages.success(request, f'Notitie "{title}" is verwijderd.')
        return redirect("notes:list")

    # GET -> confirmpagina tonen
    return render(
        request,
        "notes/confirm_delete.html",
        {
            "note": note,
        },
    )


def duplicate_note(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Maak een kopie van een bestaande Note (incl. tags).
    - GET: toon confirm-scherm
    - POST: maak duplicaat en redirect naar detail van de nieuwe
    """
    original = get_object_or_404(Note, pk=pk)

    if request.method == "POST":
        # Maak nieuwe note met prefix "Kopie van ..."
        new_note = Note.objects.create(
            title=f"Kopie van {original.title}",
            body=original.body,
        )
        # Kopieer tags mee
        new_note.tags.set(original.tags.all())

        messages.success(
            request,
            f'Notitie "{original.title}" is gedupliceerd als "{new_note.title}".',
        )
        return redirect("notes:detail", pk=new_note.pk)

    # GET -> confirmpagina tonen
    return render(
        request,
        "notes/confirm_duplicate.html",
        {
            "note": original,
        },
    )


def list_notes(request: HttpRequest) -> HttpResponse:
    """
    Toon een lijst met notities, met optionele filters:
    - ?tag=werk   -> filter op tagnaam
    - ?q=tekst    -> filter op titel/body (case-insensitive)
    Ze mogen gecombineerd worden.
    """
    tag_filter = request.GET.get("tag")
    query = request.GET.get("q")

    base_qs = Note.objects.all().prefetch_related(
        Prefetch("tags", queryset=Tag.objects.order_by("name"))
    )

    # filter op tag
    if tag_filter:
        base_qs = base_qs.filter(tags__name__iexact=tag_filter)

    # filter op zoekterm q (in titel of body)
    if query:
        base_qs = base_qs.filter(Q(title__icontains=query) | Q(body__icontains=query))

    # distinct() is belangrijk als meerdere filters overlappen dezelfde note
    notes = base_qs.distinct()

    all_tags = Tag.objects.order_by("name")

    context = {
        "notes": notes,
        "active_tag": tag_filter,
        "all_tags": all_tags,
        "q": query or "",
    }
    return render(request, "notes/list.html", context)


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


@csrf_exempt
def api_new_note(request: HttpRequest) -> JsonResponse:
    """
    Simpele JSON API endpoint om een Note + tags aan te maken.
    Authenticatie: header X-API-KEY moet overeenkomen met settings.API_KEY.
    Body (JSON):
    {
      "title": "...",
      "body": "...",
      "tags": ["werk", "privé"]
    }
    Returns:
      201 + {"id": ..., "title": ..., "tags": [...]} bij succes
      400 bij invalid input
      403 bij ontbrekende/verkeerde key
    """
    # alleen POST toegestaan
    if request.method != "POST":
        return HttpResponseBadRequest("Use POST")

    # check API key
    client_key = request.headers.get("X-API-KEY", "")
    if client_key != settings.API_KEY:
        return HttpResponseForbidden("Invalid API key")

    # parse JSON
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    title = payload.get("title", "").strip()
    body = payload.get("body", "").strip()
    tags_in = payload.get("tags", [])

    if not title:
        return HttpResponseBadRequest("Missing title")

    # maak Note
    note = Note.objects.create(title=title, body=body)

    # koppel tags indien opgegeven
    # voor elke tagnaam (bv. "werk"):
    #   - haal bestaande Tag op of maak nieuwe
    tag_objs = []
    for tag_name in tags_in:
        tag_name = str(tag_name).strip()
        if not tag_name:
            continue
        tag_obj, _created = Tag.objects.get_or_create(name=tag_name)
        tag_objs.append(tag_obj)
    if tag_objs:
        note.tags.set(tag_objs)

    data = {
        "id": note.id,
        "title": note.title,
        "tags": [t.name for t in note.tags.all()],
    }
    return JsonResponse(data, status=201)
