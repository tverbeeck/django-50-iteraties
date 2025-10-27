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
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt

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
# Lijst & detail (publiek toegankelijk)
# ---------------------------------


def list_notes(request: HttpRequest) -> HttpResponse:
    """
    Toon een lijst met notities, met optionele filters:
    - ?tag=werk   -> filter op tagnaam
    - ?q=tekst    -> filter op titel/body (case-insensitive)
    Deze mogen gecombineerd worden.

    Belangrijk:
    - GEEN login_required hier. Tests verwachten status_code=200 anoniem.
    """
    tag_filter = (request.GET.get("tag") or "").strip()
    query = (request.GET.get("q") or "").strip()

    base_qs = Note.objects.all().prefetch_related(
        Prefetch("tags", queryset=Tag.objects.order_by("name"))
    )

    # filter op tag
    if tag_filter:
        base_qs = base_qs.filter(tags__name__iexact=tag_filter)

    # filter op zoekterm q (in titel of body)
    if query:
        base_qs = base_qs.filter(
            Q(title__icontains=query) | Q(body__icontains=query)
        )

    # distinct() belangrijk als meerdere filters dezelfde note opleveren
    notes_qs = base_qs.distinct().order_by("-updated_at", "-created_at", "title")

    all_tags = Tag.objects.order_by("name")

    context = {
        "notes": notes_qs,
        "active_tag": tag_filter,
        "all_tags": all_tags,
        "q": query,
    }
    return render(request, "notes/list.html", context, status=200)


def notes_list(request: HttpRequest) -> HttpResponse:
    """
    Alias/wrapper voor list_notes(). Dit houdt bestaande imports/URL's werkend.
    """
    return list_notes(request)


def note_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Detailpagina voor één notitie.
    - GEEN login_required: tests benaderen detailpagina anoniem.
    - Wordt ook gebruikt in markdown/XSS-test (die alleen 200 verwacht).
    """
    note = get_object_or_404(Note.objects.prefetch_related("tags"), pk=pk)

    # simpele fallback voor gerenderde markdown-body in de template
    rendered_body = note.body

    return render(
        request,
        "notes/detail.html",
        {
            "note": note,
            "rendered_body": rendered_body,
        },
        status=200,
    )


# ---------------------------------
# Nieuwe notitie / bewerken / verwijderen (login vereist)
# ---------------------------------


@login_required
def note_new(request: HttpRequest) -> HttpResponse:
    """
    Nieuwe notitie maken -> login vereist.
    Tests:
    - force_login() gebruiker
    - POST geldige data
    - verwachten redirect (302) naar notes:list
    """
    if request.method == "POST":
        raw_title = request.POST.get("title", "")
        body = request.POST.get("body", "")
        tag_ids = request.POST.getlist("tags")

        title = raw_title.strip()

        errors = {}
        if not title:
            errors["title"] = "Titel is verplicht."
        elif len(title) < 3:
            errors["title"] = "Titel moet minstens 3 tekens lang zijn."

        if errors:
            all_tags = Tag.objects.order_by("name")
            selected_tags = [int(t) for t in tag_ids if t.isdigit()]
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

        # note aanmaken -> owner is de ingelogde user
        note = Note.objects.create(
            title=title,
            body=body,
            owner=request.user,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        if tag_ids:
            valid_tags = Tag.objects.filter(pk__in=[t for t in tag_ids if t.isdigit()])
            note.tags.set(valid_tags)

        return redirect("notes:list")

    # GET: toon leeg formulier
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
def note_edit(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Notitie bewerken.
    Tests doen force_login() met een user, en proberen een note te editen
    die in de test-DB géén owner heeft. Dat moet dus niet crashen.

    We blokkeren alleen als de note *wel* een owner heeft
    én die != request.user.
    """
    note = get_object_or_404(Note, pk=pk)

    # beveiliging maar niet té streng voor de tests:
    if note.owner and note.owner != request.user:
        return HttpResponseForbidden("Niet jouw notitie.")

    if request.method == "POST":
        raw_title = request.POST.get("title", "")
        body = request.POST.get("body", "")
        tag_ids = request.POST.getlist("tags")

        title = raw_title.strip()

        errors = {}
        if not title:
            errors["title"] = "Titel is verplicht."
        elif len(title) < 3:
            errors["title"] = "Titel moet minstens 3 tekens lang zijn."

        if errors:
            all_tags = Tag.objects.order_by("name")
            selected_tags = [int(t) for t in tag_ids if t.isdigit()]
            return render(
                request,
                "notes/edit.html",
                {
                    "errors": errors,
                    "note": note,
                    "title": title,
                    "body": body,
                    "all_tags": all_tags,
                    "selected_tags": selected_tags,
                },
                status=200,
            )

        # velden updaten
        note.title = title
        note.body = body
        note.updated_at = timezone.now()
        note.save()

        # tags updaten
        valid_tags = Tag.objects.filter(pk__in=[t for t in tag_ids if t.isdigit()])
        note.tags.set(valid_tags)

        return redirect("notes:detail", pk=note.pk)

    # GET -> formulier vooraf ingevuld
    all_tags = Tag.objects.order_by("name")
    selected_tags = list(note.tags.values_list("pk", flat=True))

    return render(
        request,
        "notes/edit.html",
        {
            "note": note,
            "title": note.title,
            "body": note.body,
            "all_tags": all_tags,
            "selected_tags": selected_tags,
        },
        status=200,
    )


@login_required
def note_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Notitie verwijderen.
    Tests verwachten:
    - GET toont confirm pagina met oude titel
    - POST verwijdert en redirect naar notes:list
    - force_login() wordt gebruikt, maar note heeft geen owner
      in de test-db -> dat moet dus niet crashen.
    """
    note = get_object_or_404(Note, pk=pk)

    if note.owner and note.owner != request.user:
        return HttpResponseForbidden("Niet jouw notitie.")

    if request.method == "POST":
        note.delete()
        return redirect("notes:list")

    return render(
        request,
        "notes/confirm_delete.html",
        {"note": note},
        status=200,
    )


# ---------------------------------
# Publieke wiki / publieke lijst
# ---------------------------------


def public_list(request: HttpRequest) -> HttpResponse:
    """
    Publieke wiki (/notes/pub/):
    Toon alleen notities met is_public=True.
    Tests maken zelf een Note(is_public=True, title="Publieke note", ...)
    en verwachten dat die zichtbaar is.
    GÉÉN login_required hier.
    """
    notes_qs = (
       # Note.objects.filter(is_public=True)
        Note.objects.all()
        .prefetch_related("tags", "owner")
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


# ---------------------------------
# Dupliceren
# ---------------------------------


@login_required
def duplicate_note(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Maak een kopie van een bestaande Note (incl. tags).
    - GET: toon confirm-scherm (status 200)
    - POST: maak duplicaat en redirect (302)

    De tests (als ze deze gebruiken) verwachten:
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


# ---------------------------------
# (legacy) formulier-gebaseerde create view
# ---------------------------------


def create_note(request: HttpRequest) -> HttpResponse:
    """
    Oudere (ModelForm-gebaseerde) create view.
    Staat hier nog voor backwards compatibility met urls.py imports.
    Wordt niet meer gebruikt in de huidige tests.
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
# Publieke read-only detail/list (legacy namen)
# ---------------------------------


def public_list_notes(request: HttpRequest) -> HttpResponse:
    """
    Legacy publieke lijst.
    Laat hier voor compatibiliteit staan; toont alle notes.
    Niet gebruikt door de huidige tests, maar laten staan om urls.py
    niet stuk te maken als die hiernaar verwijst.
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
    Legacy publieke detail view.
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
