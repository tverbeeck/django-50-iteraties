"""
Tests voor tag-filtering op de notitielijst.
We bouwen zelf de testdata in setUp(), dus we vertrouwen niet op fixtures.
"""

from django.test import TestCase
from django.urls import reverse
from notes.models import Note, Tag


class NotesFilterTests(TestCase):
    def setUp(self):
        # Maak tags aan
        self.tag_werk = Tag.objects.create(name="werk")
        self.tag_prive = Tag.objects.create(name="privé")

        # Maak drie notes aan
        self.note1 = Note.objects.create(title="Eerste note (werk)", body="body1")
        self.note2 = Note.objects.create(title="Tweede note (privé)", body="body2")
        self.note3 = Note.objects.create(title="Derde note (geen tags)", body="body3")

        # Koppel tags aan de eerste twee notes
        self.note1.tags.set([self.tag_werk])
        self.note2.tags.set([self.tag_prive])
        # note3.tags blijft leeg

    def test_no_filter_shows_all_notes(self):
        """Zonder ?tag=... moeten we alle notes zien."""
        url = reverse("notes:list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        # alle titels zichtbaar
        self.assertContains(resp, self.note1.title)
        self.assertContains(resp, self.note2.title)
        self.assertContains(resp, self.note3.title)

        # filter UI bevat bekende tags
        self.assertContains(resp, "?tag=werk")
        self.assertContains(resp, "?tag=priv%C3%A9")  # privé URL-encoded

    def test_filter_werk_shows_only_notes_with_werk(self):
        """Met ?tag=werk mag alleen note1 zichtbaar zijn."""
        url = reverse("notes:list") + "?tag=werk"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        # note1 heeft "werk"
        self.assertContains(resp, self.note1.title)

        # de andere niet
        self.assertNotContains(resp, self.note2.title)
        self.assertNotContains(resp, self.note3.title)

        # boodschap 'Gefilterd op tag'
        self.assertContains(resp, "Gefilterd op tag:")
        self.assertContains(resp, "werk")

    def test_filter_unknown_tag_shows_empty_message(self):
        """Met ?tag=bestaatniet moet de pagina zeggen dat er geen notities zijn."""
        url = reverse("notes:list") + "?tag=bestaatniet"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        self.assertContains(resp, "Geen notities met tag")
        # geen van de bestaande notes zou moeten verschijnen
        self.assertNotContains(resp, self.note1.title)
        self.assertNotContains(resp, self.note2.title)
        self.assertNotContains(resp, self.note3.title)

    def test_search_q_filters_by_title_or_body(self):
        """
        ?q=body2 moet note2 laten zien (want body2 zit daarin),
        maar niet noodzakelijk note1/note3.
        """
        url = reverse("notes:list") + "?q=body2"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        self.assertContains(resp, self.note2.title)
        self.assertNotContains(resp, self.note1.title)
        self.assertNotContains(resp, self.note3.title)

        self.assertContains(resp, "Zoekterm:")
        self.assertContains(resp, "body2")

    def test_search_q_combined_with_tag(self):
        """
        ?tag=werk&q=body1:
        - note1 heeft tag 'werk' en body1 -> zichtbaar
        - note2 heeft 'privé' dus niet
        - note3 heeft geen tag
        """
        url = reverse("notes:list") + "?tag=werk&q=body1"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        self.assertContains(resp, self.note1.title)
        self.assertNotContains(resp, self.note2.title)
        self.assertNotContains(resp, self.note3.title)

        self.assertContains(resp, "Gefilterd op tag:")
        self.assertContains(resp, "werk")
        self.assertContains(resp, "Zoekterm:")
        self.assertContains(resp, "body1")
