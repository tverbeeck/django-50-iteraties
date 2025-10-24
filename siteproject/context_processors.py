"""
Globale contextvariabelen voor templates.

Deze docstrings worden later gebruikt om wiki-achtige HTML te genereren.
"""

from datetime import date


def site_meta(request):
    """
    site_meta(request) -> dict
    Levert globale metadata aan elke template.

    Returns:
        dict: SITE_NAME en YEAR
    """
    return {
        "SITE_NAME": "Django 50 iteraties",
        "YEAR": date.today().year,
    }
