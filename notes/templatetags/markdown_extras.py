"""
markdown_extras
================
Template filter `markdownify` dat Markdown (met codeblokken, lijsten, tables, ...)
rendert naar veilige HTML.

We doen:
1. render Markdown -> HTML met python-markdown, met veel nuttige extensies
2. schoonmaken + whitelisten met bleach zodat er geen XSS door kan
3. linkify (maak kale URLs klikbaar)
4. mark_safe zodat Django het niet ontsnapt in de template

We laten o.a. toe:
- p, br, strong/b, em/i, code, pre, blockquote
- ul/ol/li
- h1..h6
- a (met href)
- hr
- table, thead, tbody, tr, th, td (voor Markdown-tabellen)
"""

from django import template
from django.utils.safestring import mark_safe

import markdown
import bleach

register = template.Library()

# Welke HTML-tags zijn toegestaan na de Markdown-render
ALLOWED_TAGS = [
    # text / layout
    "p",
    "br",
    "hr",
    "strong",
    "b",
    "em",
    "i",
    "code",
    "pre",
    "blockquote",
    "ul",
    "ol",
    "li",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "a",
    # tabellen (markdown 'tables' extension)
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
    # voor code highlighting
    "span",
]

# Welke HTML-attributen mogen in die tags voorkomen
ALLOWED_ATTRS = {
    "a": ["href", "title", "rel"],
    "code": ["class"],  # bv. <code class="language-python">
    "span": ["class"],  # pygments voegt vaak <span class="k"> etc. toe
    "th": ["align"],
    "td": ["align"],
    "p": ["align"],
}

ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


def _render_markdown_to_clean_html(text: str) -> str:
    """
    Neem rauwe Markdown-tekst en geef veilige HTML terug.
    """
    raw = text or ""

    # 1. Markdown -> HTML
    # We zetten veelgebruikte extensies aan:
    # - extra: tables, fenced_code, etc.
    # - codehilite: syntax highlighting markup
    # - toc: anchors voor koppen
    # - sane_lists / smarty: mooiere lijsten en typografie
    html = markdown.markdown(
        raw,
        extensions=[
            "extra",  # tables, fenced code blocks, etc.
            "codehilite",  # <pre><code class="..."> + spans for pygments
            "toc",  # table-of-contents anchors (ids op headings)
            "sane_lists",
            "smarty",
        ],
        output_format="html5",
    )

    # 2. Bleach clean -> whitelist tags/attrs/protocols, strip alles gevaarlijks
    cleaned = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )

    # 3. Linkify: auto-detect plain links en maak er <a href="..."> van
    #    (bleach.linkify is ook XSS-aware)
    linkified = bleach.linkify(cleaned)

    # 4. mark_safe: nu is het HTML waarvan we net hebben gezegd "dit is schoon"
    return mark_safe(linkified)


@register.filter
def markdownify(value: str) -> str:
    """
    Django template filter:
        {{ note.body|markdownify }}
    """
    return _render_markdown_to_clean_html(value)
