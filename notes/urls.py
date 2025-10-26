from django.urls import path
from .views import (
    list_notes,
    note_new,  # <— belangrijk
    detail_note,
    edit_note,
    delete_note,
    duplicate_note,
    public_list_notes,
    public_detail_note,
    api_list_notes,
    api_new_note,
)

urlpatterns = [
    # lijst + zoeken/filter
    path("", list_notes, name="list"),
    # nieuwe note (login required + custom validatie)
    path("new/", note_new, name="new"),
    # detail / edit / delete / duplicate
    path("<int:pk>/", detail_note, name="detail"),
    path("<int:pk>/edit/", edit_note, name="edit"),
    path("<int:pk>/delete/", delete_note, name="delete"),
    path("<int:pk>/duplicate/", duplicate_note, name="duplicate"),
    # publieke read-only views
    path("pub/", public_list_notes, name="public_list"),
    path("pub/<int:pk>/", public_detail_note, name="public_detail"),
    # simpele JSON API
    path("api/list/", api_list_notes, name="api_list"),
    path("api/new/", api_new_note, name="api_new"),
]
