"""
Tests voor Markdown rendering en XSS-sanitizing.
"""

from django.test import TestCase
from django.urls import reverse
from notes.models import Note


class MarkdownRenderTests(TestCase):
    def test_markdown_is_rendered_and_script_is_sanitized(self):
        # body bevat markdown en een kwaadaardig script
        md_body = (
            "# Titel\n\n"
            "Hier is **vet** en `inline code`.\n\n"
            "<script>alert('xss');</script>\n\n"
            "```python\nprint('hello')\n```"
        )

        note = Note.objects.create(
            title="MD test",
            body=md_body,
        )

        resp = self.client.get(reverse("notes:detail", args=[note.pk]))
        self.assertEqual(resp.status_code, 200)

        html = resp.content.decode("utf-8")

        # 1) Bold moet omgezet zijn naar <strong>vet</strong>
        self.assertIn("<strong>vet</strong>", html)

        # 2) Inline code moet gerenderd worden in <code>...</code>
        #    ('inline code' uit de backticks)
        self.assertIn("<code>inline code</code>", html)

        # 3) Codeblock zou als <pre> moeten bestaan (codehilite mag <code> weglaten)
        self.assertIn("<pre", html)

        # 4) <script> tags zelf mogen NIET meer aanwezig zijn
        #    De letterlijke tekst alert('xss') mag nog wel als gewone tekst verschijnen,
        #    want dat is niet uitvoerbaar JavaScript meer.
        self.assertNotIn("<script", html)

        # 5) De titel van de note (bovenaan via <h1>{{ note.title }}) staat er nog
        self.assertIn("MD test", html)
