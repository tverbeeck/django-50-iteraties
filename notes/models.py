"""
notes.models
============

Klein voorbeeldmodel voor notities, gebruikt in views, admin en tests.
De docstrings worden later gebruikt om wiki-achtige HTML te genereren.
"""

from django.db import models


class Note(models.Model):
    """Korte notitie met titel, optionele tekst en aanmaakdatum."""

    title = models.CharField("titel", max_length=120, help_text="Korte titel")
    body = models.TextField(
        "inhoud", blank=True, help_text="Vrije tekst (Markdown toegestaan)"
    )
    created_at = models.DateTimeField("aangemaakt op", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        """Stringrepresentatie, getoond in admin/shell."""
        return self.title
