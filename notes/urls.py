from django.urls import path
from .views import (
    list_notes,
    create_note,
    detail_note,
    edit_note,
    delete_note,
    duplicate_note,
    public_list_notes,
    public_detail_note,
    api_list_notes,
    api_new_note,
)

app_name = "notes"
urlpatterns = [
    path("", list_notes, name="list"),
    path("new/", create_note, name="new"),
    path("<int:pk>/", detail_note, name="detail"),
    path("<int:pk>/edit/", edit_note, name="edit"),
    path("<int:pk>/delete/", delete_note, name="delete"),
    path("<int:pk>/duplicate/", duplicate_note, name="duplicate"),
    # publieke read-only routes
    path("pub/", public_list_notes, name="public_list"),
    path("pub/<int:pk>/", public_detail_note, name="public_detail"),
    # API endpoints
    path("api/new/", api_new_note, name="api_new"),
    path("api/list/", api_list_notes, name="api_list"),
]
