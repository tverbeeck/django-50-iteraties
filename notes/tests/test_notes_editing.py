from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.models import Note, Tag


User = get_user_model()


class NoteEditingTests(TestCase):
    def setUp(self):
        # login vereisten oplossen
        self.user = User.objects.create_user(username="edituser", password="pass12345")
        self.client.force_login(self.user)

        # maak wat tags
        self.t_work = Tag.objects.create(name="werk")
        self.t_priv = Tag.objects.create(name="privé")

        # maak een note met beide tags
        self.note = Note.objects.create(
            title="Oude titel",
            body="Oude body **in markdown**",
        )
        self.note.tags.add(self.t_work, self.t_priv)

    def test_edit_note_updates_fields_and_tags(self):
        url = reverse("notes:edit", args=[self.note.pk])

        old_updated = self.note.updated_at

        updated_data = {
            "title": "Nieuwe titel",
            "body": "Nieuwe **body** in markdown",
            # we houden enkel de eerste tag nu
            "tags": [str(self.t_work.pk)],
        }

        resp = self.client.post(url, data=updated_data)
        # edit view zou redirecten naar detail
        self.assertEqual(resp.status_code, 302)

        # DB herladen
        self.note.refresh_from_db()

        # titel/body aangepast?
        self.assertEqual(self.note.title, "Nieuwe titel")
        self.assertIn("Nieuwe **body**", self.note.body)

        # updated_at moet verhoogd zijn
        self.assertTrue(self.note.updated_at >= old_updated)

        # tags opnieuw ingesteld?
        self.assertQuerySetEqual(
            self.note.tags.order_by("name"),
            Tag.objects.filter(pk=self.t_work.pk).order_by("name"),
            transform=lambda x: x,
        )

    def test_delete_note_removes_it(self):
        url = reverse("notes:delete", args=[self.note.pk])

        # GET zou confirm tonen (nu login_required opgelost door force_login)
        resp_get = self.client.get(url)
        self.assertEqual(resp_get.status_code, 200)
        self.assertContains(resp_get, "Weet je zeker dat je wilt verwijderen")

        # POST zou deleten en redirecten naar lijst
        resp_post = self.client.post(url)
        self.assertEqual(resp_post.status_code, 302)
        self.assertEqual(resp_post["Location"], reverse("notes:list"))
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_duplicate_note_creates_copy_with_same_body_and_tags(self):
        url = reverse("notes:duplicate", args=[self.note.pk])

        # GET toont confirm
        resp_get = self.client.get(url)
        self.assertEqual(resp_get.status_code, 200)
        self.assertContains(resp_get, "dupliceren")

        # POST maakt kopie
        resp_post = self.client.post(url)
        self.assertEqual(resp_post.status_code, 302)

        # er moeten nu 2 notes zijn
        all_notes = Note.objects.order_by("pk")
        self.assertEqual(all_notes.count(), 2)

        original = all_notes[0]
        dupe = all_notes[1]

        # body gekopieerd
        self.assertEqual(dupe.body, original.body)

        # tags gekopieerd
        self.assertQuerySetEqual(
            dupe.tags.order_by("name"),
            original.tags.order_by("name"),
            transform=lambda x: x,
        )

        # slug van de kopie moet verschillend zijn
        self.assertNotEqual(original.slug, dupe.slug)
