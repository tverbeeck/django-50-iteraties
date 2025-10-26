"""
Tests voor de detailpagina en het JSON-list endpoint.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.models import Note

User = get_user_model()


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
    def setUp(self):
        self.user = User.objects.create_user(username="normuser", password="pw12345")
        self.client.force_login(self.user)

    def test_title_is_normalized_and_validated(self):
        # Post met extra spaties en korte titel checken
        url = reverse("notes:new")
        resp = self.client.post(path=url, data={"title": "  A ", "body": "x"})
        # Titel te kort -> fout, dus geen redirect (status_code=200) en foutmelding aanwezig
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "minstens 3 tekens")

        # nu met geldige titel met spaties errond
        resp2 = self.client.post(
            path=url, data={"title": "  Geldige titel  ", "body": "ok"}
        )
        # nu verwachten we redirect (302) en dat de note bestaat met opgeschoonde titel
        self.assertEqual(resp2.status_code, 302)

        n = Note.objects.latest("pk")
        self.assertEqual(n.title, "Geldige titel")  # gestript
        self.assertTrue(n.slug)
