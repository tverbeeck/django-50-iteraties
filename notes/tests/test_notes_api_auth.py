import json
from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from notes.models import Note


class ApiAuthTests(TestCase):
    def test_requires_api_key(self):
        """
        Zonder X-API-KEY moeten we 403 Forbidden krijgen.
        """
        url = reverse("notes:api_new")
        resp = self.client.post(
            url,
            data=json.dumps(
                {
                    "title": "Zonder key",
                    "body": "zou niet mogen werken",
                    "tags": ["geheim"],
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Note.objects.count(), 0)

    def test_rejects_wrong_api_key(self):
        """
        Met een foute key ook 403.
        """
        url = reverse("notes:api_new")
        resp = self.client.post(
            url,
            data=json.dumps(
                {
                    "title": "Foute key",
                    "body": "nope",
                    "tags": ["werk"],
                }
            ),
            content_type="application/json",
            HTTP_X_API_KEY="totally-wrong-key",
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Note.objects.count(), 0)

    def test_creates_note_with_valid_key(self):
        """
        Met de juiste key: 201 + note wordt aangemaakt incl. tags.
        """
        url = reverse("notes:api_new")
        resp = self.client.post(
            url,
            data=json.dumps(
                {
                    "title": "Aangemaakt via API",
                    "body": "Dit kwam van een client",
                    "tags": ["werk", "privé"],
                }
            ),
            content_type="application/json",
            HTTP_X_API_KEY=settings.API_KEY,  # geldige sleutel
        )

        self.assertEqual(resp.status_code, 201)

        # controleer dat de note in de DB bestaat
        self.assertEqual(Note.objects.count(), 1)
        n = Note.objects.first()
        self.assertEqual(n.title, "Aangemaakt via API")
        self.assertIn("werk", [t.name for t in n.tags.all()])
        self.assertIn("privé", [t.name for t in n.tags.all()])

        # en dat de JSON response de juiste data bevat
        payload = resp.json()
        self.assertIn("id", payload)
        self.assertEqual(payload["title"], "Aangemaakt via API")
        self.assertIn("werk", payload["tags"])
        self.assertIn("privé", payload["tags"])
