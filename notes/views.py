"""
notes.views
===========

Views voor het notitie-overzicht.
"""
from django.shortcuts import render
from .models import Note

def list_notes(request):
    """
    Toon een eenvoudige lijst met notities.
    """
    notes = Note.objects.all()
    return render(request, "notes/list.html", {"notes": notes})

