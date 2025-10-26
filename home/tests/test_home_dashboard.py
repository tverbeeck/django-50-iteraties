from django.test import TestCase
from django.urls import reverse
from notes.models import Note, Tag


class HomeDashboardTests(TestCase):
    def test_home_shows_recent_notes_and_tags(self):
        """
        De homepage (dashboard) moet:
        - recente notities tonen
        - tags tonen
        - een link hebben naar publieke wiki
        """

        # Arrange: maak wat data
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
        url = reverse("home")  # dit is path("", dashboard_home, name="home")
        resp = self.client.get(url)

        # Assert: status OK
        self.assertEqual(resp.status_code, 200)

        html = resp.content.decode("utf-8")

        # 1. notitietitels zichtbaar
        self.assertIn("Note 1", html)
        self.assertIn("Note 2", html)

        # 2. tagnaam zichtbaar
        self.assertIn("dashboardtag", html)

        # 3. TagLink bevat ?tag=dashboardtag
        self.assertIn("tag=dashboardtag", html)

        # 4. Publieke wiki-link zichtbaar (onze eigen tekst)
        self.assertIn("Publieke wiki", html)

        # 5. De juiste URL naar de publieke lijst zit erin
        public_url = reverse("notes:public_list")  # dit is bv. "/notes/pub/"
        self.assertIn(public_url, html)
