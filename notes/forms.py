"""
notes.forms
===========

ModelForm voor het aanmaken/bewerken van Note-objecten.
De docstrings worden later gebruikt voor wiki-achtige HTML.
"""

from django import forms
from .models import Note, Tag


class NoteForm(forms.ModelForm):
    """Formulier gebaseerd op het Note-model."""

    class Meta:
        model = Note
        fields = ["title", "body", "tags"]
        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": "Titel", "autofocus": "autofocus"}
            ),
            "body": forms.Textarea(
                attrs={"rows": 6, "placeholder": "Inhoud (markdown mag)"}
            ),
            "tags": forms.CheckboxSelectMultiple,
        }
        help_texts = {
            "title": "Korte titel voor de notitie.",
            "body": "Optioneel. Je kunt later markdown parsers toevoegen.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # queryset dynamisch (efficiënt bij latere filtering)
        self.fields["tags"].queryset = Tag.objects.all()

    def clean_title(self):
        """
        Normaliseer de titel:
        - trim witruimte
        - reduceer interne whitespace tot één spatie
        - valideer minimale lengte 3
        """
        title = self.cleaned_data.get("title", "")
        # strip en normaliseer spaties
        title = " ".join(title.split())
        if len(title) < 3:
            raise forms.ValidationError("Titel moet minstens 3 tekens bevatten.")
        return title
