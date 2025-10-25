from django.contrib import admin
from .models import Note, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name",)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")
    search_fields = ("title", "body")
    list_filter = ("created_at", "tags")
    filter_horizontal = ("tags",)  # makkelijke multi-select
    ordering = ("-created_at",)
