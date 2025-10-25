"""
notes.models
============

Klein voorbeeldmodel voor notities, gebruikt in views, admin en tests.
De docstrings worden later gebruikt om wiki-achtige HTML te genereren.
Definitie van Note en Tag.
Tag = label dat je kan koppelen aan meerdere Notes (ManyToMany).
"""

from django.db import models


class Tag(models.Model):
    """Eenvoudig label om notities te groeperen/filtreren."""

    name = models.CharField("naam", max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class Note(models.Model):
    """Korte notitie met titel, optionele tekst en aanmaakdatum."""

    title = models.CharField("titel", max_length=120, help_text="Korte titel")
    body = models.TextField(
        "inhoud", blank=True, help_text="Vrije tekst (Markdown toegestaan)"
    )
    created_at = models.DateTimeField("aangemaakt op", auto_now_add=True)

    # <<< Dit veld MOET er zijn voor de ManyToMany-relatie >>>
    tags = models.ManyToManyField(
        Tag, related_name="notes", blank=True, verbose_name="tags"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        """Stringrepresentatie, getoond in admin/shell."""
        return self.title
