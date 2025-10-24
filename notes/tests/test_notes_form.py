"""
Tests voor het aanmaken van notities via het formulier.
"""
from django.test import TestCase
from django.urls import reverse
from notes.models import Note

class NoteFormTests(TestCase):
    def test_get_new_form(self):
        """GET /notes/new/ toont het formulier."""
        url = reverse("notes:new")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "<form", html=False)
        self.assertContains(resp, "Nieuwe notitie")

    def test_post_valid_creates_note_and_redirects(self):
        """POST met geldige data maakt een Note aan en redirect naar de lijst met message."""
        url = reverse("notes:new")
        data = {"title": "Form note", "body": "Toegevoegd via test."}
        resp = self.client.post(url, data, follow=True)  # follow om redirect + messages te zien
        self.assertRedirects(resp, reverse("notes:list"), fetch_redirect_response=False)
        self.assertTrue(Note.objects.filter(title="Form note").exists())
        # message zichtbaar?
        self.assertContains(resp, "Notitie is toegevoegd.")

    def test_post_invalid_shows_errors(self):
        """POST met ongeldige data (lege titel) toont fouten en maakt niets aan."""
        url = reverse("notes:new")
        resp = self.client.post(url, {"title": "", "body": "x"})
        self.assertEqual(resp.status_code, 200)  # geen redirect, terug naar form
        self.assertContains(resp, "Dit veld is verplicht", html=False)
        self.assertEqual(Note.objects.count(), 0)
