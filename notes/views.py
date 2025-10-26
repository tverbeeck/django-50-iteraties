"""
notes.views
===========

Views voor notities (lijst, detail, aanmaken, API, ...).
Bevat ook tag-weergave en publieke read-only views.
"""

import json
from typing import List

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q
from django.http import (
    HttpRequest,
    HttpResponse,
    JsonResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .forms import NoteForm
from .models import Note, Tag


# ---------------------------------
# helpers
# ---------------------------------


def _normalize_title(raw_title: str) -> str:
    """Strips whitespace en normaliseert titel."""
    return (raw_title or "").strip()


def _ensure_unique_slug(note: Note) -> None:
    """
    Zorg dat note.slug bestaat en uniek is.
    - Als model.save() dit al garandeert, prima.
    - Anders genereren we hier een slug op basis van de titel.
    """
    if note.slug:
        return

    base = slugify(note.title)[:50] or "note"
    candidate = base
    i = 2
    # probeer telkens nieuwe kandidaat tot hij uniek is
    while Note.objects.filter(slug=candidate).exclude(pk=note.pk).exists():
        candidate = f"{base}-{i}"[:60]
        i += 1

    note.slug = candidate
    note.save(update_fields=["slug"])


# ---------------------------------
# CRUD / formulieren
# ---------------------------------


@login_required
def note_new(request):
    if request.method == "POST":
        # 1. raw data ophalen
        raw_title = request.POST.get("title", "")
        body = request.POST.get("body", "")
        tag_ids = request.POST.getlist("tags")

        # 2. normaliseren
        title = raw_title.strip()

        # 3. eenvoudige validatie
        errors = {}
        if not title:
            errors["title"] = "Titel is verplicht."
        elif len(title) < 3:
            errors["title"] = "Titel moet minstens 3 tekens lang zijn."

        if errors:
            # VALIDATIE MISLUKT -> toon formulier opnieuw, status 200
            all_tags = Tag.objects.order_by("name")
            selected_tags = [int(tid) for tid in tag_ids if tid.isdigit()]

            return render(
                request,
                "notes/new.html",
                {
                    "errors": errors,
                    "title": title,
                    "body": body,
                    "all_tags": all_tags,
                    "selected_tags": selected_tags,
                },
                status=200,
            )

        # 4. VALIDATIE OK -> note opslaan
        note = Note.objects.create(
            title=title,
            body=body,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        # tags koppelen (niet strikt nodig voor de tests, maar netjes)
        if tag_ids:
            tags = Tag.objects.filter(
                id__in=[int(tid) for tid in tag_ids if tid.isdigit()]
            )
            note.tags.set(tags)

        # 5. redirect naar de notitie-lijst (/notes/)
        return redirect("notes:list")

    # GET-verzoek: leeg formulier tonen
    all_tags = Tag.objects.order_by("name")
    return render(
        request,
        "notes/new.html",
        {
            "errors": {},
            "title": "",
            "body": "",
            "all_tags": all_tags,
            "selected_tags": [],
        },
        status=200,
    )


@login_required
def edit_note(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Bewerk een bestaande Note.
    - GET: toon formulier vooraf ingevuld
    - POST: valideer en sla op, redirect naar detail
    De tests verwachten dat titel/body/tags effectief aangepast worden.
    """
    note = get_object_or_404(Note, pk=pk)

    if request.method == "POST":
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            updated_note = form.save()  # dit past title/body/tags aan
            # slug moet geldig blijven:
            _ensure_unique_slug(updated_note)

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
        status=200,
    )


@login_required
def delete_note(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Verwijder een bestaande Note.
    - GET: toon confirm-schermpje (status 200)
    - POST: voer de delete uit en redirect naar lijst (302)
    De tests verwachten dat GET 200 teruggeeft, geen redirect.
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
            # test zoekt o.a. naar deze tekst
            "confirm_text": "Weet je zeker dat je wilt verwijderen",
        },
        status=200,
    )


@login_required
def duplicate_note(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Maak een kopie van een bestaande Note (incl. tags).
    - GET: toon confirm-scherm (status 200)
    - POST: maak duplicaat en redirect (302)
    De tests verwachten:
      - status_code 200 bij GET
      - erna bestaan er 2 notes
      - body en tags gelijk
      - slug verschillend
    """
    original = get_object_or_404(Note, pk=pk)

    if request.method == "POST":
        # Maak nieuwe note met prefix "Kopie van ..."
        new_note = Note.objects.create(
            title=f"Kopie van {original.title}",
            body=original.body,
        )

        # tags kopiëren
        new_note.tags.set(original.tags.all())

        # slug invullen / uniek maken
        _ensure_unique_slug(new_note)

        # redirect naar detail van de nieuwe note
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
            "confirm_text": "Wil je deze notitie dupliceren?",
        },
        status=200,
    )


# ⬇⬇⬇ TERUGGEZET VOOR urls.py COMPATIBILITEIT ⬇⬇⬇
def create_note(request: HttpRequest) -> HttpResponse:
    """
    Oudere (ModelForm-gebaseerde) create view.
    Wordt niet meer gebruikt in de tests, maar notes/urls.py importeert dit nog.
    We houden dit dus om ImportError te voorkomen.
    """
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save()
            _ensure_unique_slug(note)
            messages.success(request, "Notitie is toegevoegd.")
            return redirect("notes:list")
    else:
        form = NoteForm()
    return render(request, "notes/form.html", {"form": form}, status=200)


# ---------------------------------
# Lijst / detail (privé)
# ---------------------------------


def list_notes(request: HttpRequest) -> HttpResponse:
    """
    Toon een lijst met notities, met optionele filters:
    - ?tag=werk   -> filter op tagnaam
    - ?q=tekst    -> filter op titel/body (case-insensitive)
    Deze mogen gecombineerd worden.
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
    notes_qs = base_qs.distinct()

    all_tags = Tag.objects.order_by("name")

    context = {
        "notes": notes_qs,
        "active_tag": tag_filter,
        "all_tags": all_tags,
        "q": query or "",
    }
    return render(request, "notes/list.html", context, status=200)


def detail_note(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Detailpagina voor één notitie.
    """
    note = get_object_or_404(Note.objects.prefetch_related("tags"), pk=pk)
    return render(request, "notes/detail.html", {"note": note}, status=200)


# ---------------------------------
# Simpele JSON API
# ---------------------------------


def api_list_notes(request: HttpRequest) -> JsonResponse:
    """
    JSON-endpoint met id, title, created_at en tags per note.
    Gebruikt geen auth.
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

    title = (payload.get("title") or "").strip()
    body = (payload.get("body") or "").strip()
    tags_in = payload.get("tags", [])

    if not title:
        return HttpResponseBadRequest("Missing title")

    # maak Note
    note = Note.objects.create(title=title, body=body)

    # slug invullen / uniek maken
    _ensure_unique_slug(note)

    # koppel tags indien opgegeven
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


# ---------------------------------
# Publieke read-only views
# ---------------------------------


def public_list_notes(request: HttpRequest) -> HttpResponse:
    """
    Publieke read-only lijst.
    Geen zoekveld, geen edit-acties.
    Toont alle notes gesorteerd op -updated_at (laatst bijgewerkt eerst).
    """
    notes_qs = (
        Note.objects.all()
        .prefetch_related("tags")
        .order_by("-updated_at", "-created_at", "title")
    )

    return render(
        request,
        "notes/public_list.html",
        {
            "notes": notes_qs,
        },
        status=200,
    )


def public_detail_note(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Publieke read-only detail.
    Zelfde Markdown rendering, maar zonder beheer-links.
    """
    note = get_object_or_404(
        Note.objects.prefetch_related("tags"),
        pk=pk,
    )
    return render(
        request,
        "notes/public_detail.html",
        {
            "note": note,
        },
        status=200,
    )
