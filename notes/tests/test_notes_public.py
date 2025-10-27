from django.test import TestCase
from django.urls import reverse
from notes.models import Note, Tag


class PublicViewsTests(TestCase):
    def setUp(self):
        self.tag = Tag.objects.create(name="openbaar")
        self.note = Note.objects.create(
            title="Publieke note",
            body="**Publieke** inhoud",
        )
        self.note.tags.add(self.tag)

    def test_public_list_shows_note_and_timestamp(self):
        url = reverse("notes:public_list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode("utf-8")

        # titel beschikbaar
        self.assertIn("Publieke note", html)
        # tag zichtbaar
        self.assertIn("openbaar", html)
        # bevat 'Laatst gewijzigd'
        self.assertIn("Laatst", html)
        # geen 'Nieuwe notitie'
        self.assertNotIn("Nieuwe notitie", html)

    def test_public_detail_renders_markdown_without_edit_links(self):
        url = reverse("notes:public_detail", args=[self.note.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode("utf-8")

        # note title aanwezig
        self.assertIn("Publieke note", html)
        # body gerenderd als <strong> door markdownify
        self.assertIn("<strong>Publieke</strong>", html)
        # timestamps aanwezig
        self.assertIn("Aangemaakt op:", html)
        self.assertIn("Laatst gewijzigd op:", html)

        # en heel belangrijk: geen beheer-acties
        self.assertNotIn("Bewerken", html)
        self.assertNotIn("Dupliceren", html)
        self.assertNotIn("Verwijderen", html)
