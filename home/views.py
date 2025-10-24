"""
home.views
==========

Wiki-notes:
- Landing page en About-pagina, gerenderd met templates.
- Docstrings worden later gebruikt voor wiki-achtige HTML.
"""

from django.shortcuts import render


def index(request):
    """
    Render de homepagina via 'templates/home/index.html'.
    """
    return render(request, "home/index.html")


def about(request):
    """
    Eenvoudige About-pagina.
    """
    return render(request, "home/about.html")
