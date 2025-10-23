from django.shortcuts import render

# Create your views here.

"""
home.views
==========

Wiki-notes:
- Deze module bevat de landing page van de site.
- Uitgebreide uitleg komt in latere iteraties.
"""

from django.http import HttpResponse

def index(request):
    """
    index(request) -> HttpResponse

    Een ultrakorte landing page.
    Deze docstring wordt later gebruikt door de documentatiegenerator
    om wiki-achtige HTML te maken.
    """
    return HttpResponse("Hello, Django 👋")

