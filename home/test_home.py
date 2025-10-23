"""
Tests voor de home-app.

Deze tests documenteren het verwachte gedrag van de homepage.
Ze dienen later als voorbeeld voor onze wikidocumentatie.
"""
from django.test import TestCase
from django.urls import reverse

class HomeViewTests(TestCase):
    """Tests voor de index-view."""

    def test_home_status_and_content(self):
        """De homepagina geeft status 200 en bevat de verwachte titel."""
        url = reverse("home-index")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Hello, Django")
