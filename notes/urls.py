from django.urls import path
from .views import (
    list_notes,
    create_note,
    detail_note,
    edit_note,
    delete_note,
    duplicate_note,
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
    # API endpoints
    path("api/new/", api_new_note, name="api_new"),
    path("api/list/", api_list_notes, name="api_list"),
]
