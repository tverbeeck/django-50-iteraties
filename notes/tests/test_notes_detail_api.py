"""
Tests voor de detailpagina en het JSON-list endpoint.
"""
from django.test import TestCase
from django.urls import reverse
from notes.models import Note

class NotesDetailAndApiTests(TestCase):
    fixtures = ["notes.json"]

    def test_detail_status_and_content(self):
        url = reverse("notes:detail", args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Eerste notitie")  # uit fixtures

    def test_api_list_returns_json(self):
        url = reverse("notes:api_list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/json")
        data = resp.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 2)
        self.assertIn("title", data[0])

class NotesFormNormalizationTests(TestCase):
    def test_title_is_normalized_and_validated(self):
        # Post met extra spaties en korte titel checken
        url = reverse("notes:new")
        resp = self.client.post(url, {"title": "  A ", "body": "x"})
        # Titel te kort -> fout
        self.assertContains(resp, "minstens 3 tekens", status_code=200)

        # Nu een geldige titel met veel spaties:
        resp = self.client.post(url, {"title": "  Hello   World  ", "body": ""}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Note.objects.filter(title="Hello World").exists())
