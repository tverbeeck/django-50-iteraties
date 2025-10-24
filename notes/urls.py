from django.urls import path
from .views import list_notes, create_note

app_name = "notes"
urlpatterns = [
    path("", list_notes, name="list"),
    path("new/", create_note, name="new"),
]
