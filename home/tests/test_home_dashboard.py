from django.test import TestCase
from django.urls import reverse
from notes.models import Note, Tag


class HomeDashboardTests(TestCase):
    def test_home_shows_recent_notes_and_tags(self):
        """
        De homepage (dashboard) moet:
        - recente notities tonen
        - tags tonen
        - een link hebben naar publieke wikiweergave
        """

        # Arrange: maak wat tags en notes zodat er iets te tonen valt
        t = Tag.objects.create(name="dashboardtag")

        n1 = Note.objects.create(
            title="Note 1",
            body="body1",
        )
        n1.tags.add(t)

        n2 = Note.objects.create(
            title="Note 2",
            body="body2",
        )
        n2.tags.add(t)

        # Act: vraag de homepage op
        # Belangrijk: we gebruiken reverse("home") i.p.v. reverse("home:home"),
        # omdat je project momenteel geen namespace 'home' heeft.
        url = reverse("home")
        resp = self.client.get(url)

        # Assert: status OK
        self.assertEqual(resp.status_code, 200)

        html = resp.content.decode("utf-8")

        # 1. Notitietitels zichtbaar
        self.assertIn("Note 1", html)
        self.assertIn("Note 2", html)

        # 2. Tagnaam zichtbaar
        self.assertIn("dashboardtag", html)

        # 3. Taglink bevat ?tag=dashboardtag
        self.assertIn("?tag=dashboardtag", html)

        # 4. Link of tekst naar publieke wikiweergave
        self.assertIn("Publieke wikiweergave", html)
