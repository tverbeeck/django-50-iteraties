from django.test import TestCase
from django.urls import reverse
from notes.models import Note


class NotesAuthRequiredTests(TestCase):
    def setUp(self):
        self.note = Note.objects.create(
            title="Beveiligde note",
            body="Topsecret",
        )

    def test_new_requires_login(self):
        resp = self.client.get(reverse("notes:new"))
        # niet ingelogd -> redirect naar login
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.headers["Location"])

    def test_edit_requires_login(self):
        resp = self.client.get(reverse("notes:edit", args=[self.note.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.headers["Location"])

    def test_delete_requires_login(self):
        resp = self.client.get(reverse("notes:delete", args=[self.note.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.headers["Location"])

    def test_duplicate_requires_login(self):
        resp = self.client.get(reverse("notes:duplicate", args=[self.note.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.headers["Location"])
