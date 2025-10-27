from django.urls import path
from .views import (
    notes_list,
    note_new,  # <— belangrijk
    note_detail,
    note_edit,
    note_delete,
    
    duplicate_note,
    public_list,
    public_detail_note,
    api_list_notes,
    api_new_note,
)

app_name = "notes"

urlpatterns = [
    # lijst + zoeken/filter
    path("", notes_list, name="list"), # /notes/
    # nieuwe note (login required + custom validatie)
    path("new/", note_new, name="new"), # /notes/new/
    # detail / edit / delete / duplicate
    path("<int:pk>/", note_detail, name="detail"), # /notes/5/
    path("<int:pk>/edit/", note_edit, name="edit"), # /notes/5/edit/
    path("<int:pk>/delete/", note_delete, name="delete"), # /notes/5/delete/
    path("<int:pk>/duplicate/", duplicate_note, name="duplicate"),
    # publieke read-only views
    path("pub/", public_list, name="public_list"), # /notes/pub/
    path("pub/<int:pk>/", public_detail_note, name="public_detail"),
    # simpele JSON API
    path("api/list/", api_list_notes, name="api_list"),
    path("api/new/", api_new_note, name="api_new"),
]
