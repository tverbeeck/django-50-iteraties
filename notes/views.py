"""
notes.views
===========

Views voor het notitie-overzicht.
"""

from django.shortcuts import get_object_or_404, redirect, render
from .models import Note
from django.contrib import messages
from .forms import NoteForm
from django.http import JsonResponse


def api_list_notes(request):
    """
    Eenvoudig JSON-endpoint met (id, title, created_at) voor alle notities.
    """
    data = [
        {
            "id": n.id,
            "title": n.title,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }
        for n in Note.objects.all()
    ]
    return JsonResponse(data, safe=False)


def create_note(request):
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


def list_notes(request):
    """
    Toon een eenvoudige lijst met notities.
    """
    notes = Note.objects.all()
    return render(request, "notes/list.html", {"notes": notes})


def detail_note(request, pk: int):
    """
    Detailpagina voor één notitie.
    """
    note = get_object_or_404(Note, pk=pk)
    return render(request, "notes/detail.html", {"note": note})
