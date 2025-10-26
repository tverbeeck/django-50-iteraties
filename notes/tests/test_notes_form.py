"""
Tests voor het aanmaken van notities via het formulier.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.models import Note

User = get_user_model()


class NoteFormTests(TestCase):
    def setUp(self):
        # maak en login een testuser, want /notes/new/ is nu login_required
        self.user = User.objects.create_user(
            username="formtester", password="testpass123"
        )
        self.client.force_login(self.user)

    def test_get_new_form(self):
        """GET /notes/new/ toont het formulier."""
        url = reverse("notes:new")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # bevat de velden?
        self.assertContains(resp, "<form", status_code=200)
        self.assertContains(resp, 'name="title"')
        self.assertContains(resp, 'name="body"')

    def test_post_invalid_shows_errors(self):
        """
        POST met ongeldige data (lege titel) toont fouten en maakt niets aan.
        We verwachten status_code=200 (geen redirect), én foutmelding.
        """
        url = reverse("notes:new")
        resp = self.client.post(url, {"title": "", "body": "x"})
        self.assertEqual(resp.status_code, 200)  # terug naar form
        self.assertContains(resp, "minstens 3 tekens")
        self.assertEqual(Note.objects.count(), 0)

    def test_post_valid_creates_note_and_redirects(self):
        """
        POST met geldige data maakt een Note aan en redirect naar de lijst (302),
        en uiteindelijk willen we dat redirect eindigt op /notes/.
        """
        url = reverse("notes:new")
        data = {"title": "Form note", "body": "Toegevoegd via test."}
        resp = self.client.post(url, data)
        # redirect naar lijst
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], reverse("notes:list"))

        # note werd effectief aangemaakt
        self.assertEqual(Note.objects.count(), 1)
        n = Note.objects.first()
        self.assertEqual(n.title, "Form note")
        self.assertIn("Toegevoegd via test.", n.body)
        self.assertTrue(n.slug)  # slug werd gezet
