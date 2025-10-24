"""
Tests voor de notes-app. Gebruikt fixtures/notes.json.
"""
from django.test import TestCase
from django.urls import reverse
from notes.models import Note

class NotesTests(TestCase):
    fixtures = ["notes.json"]  # geladen uit notes/fixtures/

    def test_list_status_and_content(self):
        url = reverse("notes:list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Notities")
        self.assertContains(resp, "Eerste notitie")

    def test_model_str(self):
        n = Note.objects.get(pk=1)
        self.assertEqual(str(n), "Eerste notitie")
