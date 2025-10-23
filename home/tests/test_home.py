from django.test import TestCase, override_settings
from django.urls import reverse

class HomeViewTests(TestCase):
    """Tests voor de index- en about-views."""

    def test_home_status_and_content(self):
        url = reverse("home-index")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Hello, Django")

    def test_about_status_and_content(self):
        url = reverse("home-about")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Over dit project")

class ErrorPageTests(TestCase):
    """Verifieer dat onze 404-template wordt gebruikt als DEBUG=False staat."""

    @override_settings(DEBUG=False)
    def test_404_uses_custom_template(self):
        resp = self.client.get("/bestaat-niet/")
        self.assertEqual(resp.status_code, 404)
        self.assertContains(resp, "Pagina niet gevonden (404)")
