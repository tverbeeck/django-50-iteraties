from django.test import TestCase
from django.urls import reverse
from notes.models import Note, Tag


class NoteEditingTests(TestCase):
    def setUp(self):
        # we maken een note met 2 tags
        self.t_work = Tag.objects.create(name="werk")
        self.t_ideas = Tag.objects.create(name="ideeën")

        self.note = Note.objects.create(
            title="Oude titel",
            body="Oude body",
        )
        self.note.tags.set([self.t_work, self.t_ideas])

    def test_edit_note_updates_fields_and_tags(self):
        url = reverse("notes:edit", args=[self.note.pk])

        # nieuwe data om te posten
        updated_data = {
            "title": "Nieuwe titel",
            "body": "Nieuwe **body** in markdown",
            # we houden enkel de eerste tag nu
            "tags": [str(self.t_work.pk)],
        }

        resp = self.client.post(url, data=updated_data)
        # redirect terug naar detail
        self.assertEqual(resp.status_code, 302)

        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "Nieuwe titel")
        self.assertIn("Nieuwe **body**", self.note.body)
        self.assertQuerySetEqual(
            self.note.tags.order_by("name"),
            Tag.objects.filter(pk=self.t_work.pk).order_by("name"),
            transform=lambda x: x,
        )

    def test_delete_note_removes_it(self):
        url = reverse("notes:delete", args=[self.note.pk])

        # GET zou confirm tonen
        resp_get = self.client.get(url)
        self.assertEqual(resp_get.status_code, 200)
        self.assertContains(resp_get, "Weet je zeker")

        # POST verwijdert
        resp_post = self.client.post(url)
        self.assertEqual(resp_post.status_code, 302)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_duplicate_note_creates_copy_with_same_body_and_tags(self):
        url = reverse("notes:duplicate", args=[self.note.pk])

        # GET toont confirm
        resp_get = self.client.get(url)
        self.assertEqual(resp_get.status_code, 200)
        self.assertContains(resp_get, "kopie")

        # POST maakt de kopie
        resp_post = self.client.post(url)
        self.assertEqual(resp_post.status_code, 302)

        # er zou nu een tweede Note moeten zijn
        notes = Note.objects.order_by("pk")
        self.assertEqual(notes.count(), 2)

        original = notes[0]
        copy = notes[1]

        self.assertEqual(original.title, "Oude titel")
        self.assertEqual(copy.body, original.body)
        self.assertEqual(
            list(copy.tags.order_by("name").values_list("name", flat=True)),
            list(original.tags.order_by("name").values_list("name", flat=True)),
        )
        self.assertTrue(copy.title.startswith("Kopie van "))
