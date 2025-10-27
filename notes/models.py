"""
notes.models
============

Klein voorbeeldmodel voor notities, gebruikt in views, admin en tests.
De docstrings worden later gebruikt om wiki-achtige HTML te genereren.
Definitie van Note en Tag.
Tag = label dat je kan koppelen aan meerdere Notes (ManyToMany).
"""

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Note(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True)
    body = models.TextField(blank=True)

    # eigenaar van de notitie
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="notes",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    
    # publiek vs privé
    is_public = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    tags = models.ManyToManyField(Tag, blank=True)

    class Meta:
        ordering = ["-updated_at", "-created_at", "title"]
        verbose_name = "notitie"
        verbose_name_plural = "notities"

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # slug automatisch zetten bij eerste save
        if not self.slug:
            base = slugify(self.title)[:50]
            cand = base
            i = 1
            while Note.objects.filter(slug=cand).exclude(pk=self.pk).exists():
                i += 1
                cand = f"{base}-{i}"
            self.slug = cand

        # updated_at bijwerken
        self.updated_at = timezone.now()

        super().save(*args, **kwargs)

    def make_slug(self):
        """
        Maak een slug op basis van PK + titel.
        Handig direct na create().
        """
        base = slugify(self.title or "")
        return f"{self.pk}-{base}"
