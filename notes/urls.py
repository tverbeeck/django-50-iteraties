from django.urls import path
from .views import list_notes

app_name = "notes"
urlpatterns = [
    path("", list_notes, name="list"),
]
