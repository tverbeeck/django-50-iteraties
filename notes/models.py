"""
notes.models
============

Klein voorbeeldmodel voor notities, gebruikt in views, admin en tests.
De docstrings worden later gebruikt om wiki-achtige HTML te genereren.
Definitie van Note en Tag.
Tag = label dat je kan koppelen aan meerdere Notes (ManyToMany).
"""

# notes/models.py
from django.db import models
from django.utils.text import slugify


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Note(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=220,
        blank=True,
        null=False,  # <-- finale constraint
        unique=True,  # <-- finale constraint
        help_text="URL-vriendelijke unieke naam gebaseerd op de titel.",
    )
    body = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, related_name="notes", blank=True)

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title or "note")
            candidate = base
            counter = 1
            # houd slug uniek binnen Notes
            while Note.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                counter += 1
                candidate = f"{base}-{counter}"
            self.slug = candidate
        super().save(*args, **kwargs)
