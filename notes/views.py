"""
notes.views
===========

Views voor het notitie-overzicht.
"""
from django.shortcuts import render
from .models import Note
from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import NoteForm
from .models import Note

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


