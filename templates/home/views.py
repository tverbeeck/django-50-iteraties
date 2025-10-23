"""
home.views
==========

Wiki-notes:
- Landing page van de site, gerenderd met een template.
- Deze module bevat duidelijke docstrings die later voor HTML-documentatie gebruikt worden.
"""

from django.shortcuts import render

def index(request):
    """
    index(request) -> HttpResponse

    Render de homepagina via 'templates/home/index.html'.

    Returns:
        HttpResponse: de gerenderde HTML.
    """
    return render(request, "home/index.html")

def about(request):
    """
    about(request) -> HttpResponse
    Eenvoudige About-pagina.
    """
    return render(request, "home/about.html")
