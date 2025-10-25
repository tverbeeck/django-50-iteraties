from django.shortcuts import render
from notes.models import Note, Tag


def home(request):
    """
    Dashboard / startpagina
    Toont recente notities, tags en een link naar de publieke wikiweergave.
    """
    # Recentste notities eerst. Als updated_at bestaat gebruiken we die.
    if hasattr(Note, "updated_at"):
        recent_notes = Note.objects.order_by("-updated_at")[:5]
    else:
        recent_notes = Note.objects.order_by("-created_at")[:5]

    all_tags = Tag.objects.order_by("name")

    return render(
        request,
        "home/home.html",
        {
            "recent_notes": recent_notes,
            "all_tags": all_tags,
        },
    )


def about(request):
    """
    Eenvoudige About-pagina.
    Wordt gebruikt door reverse("home-about") en {% url 'home-about' %}.
    """
    return render(request, "home/about.html")


def custom_404(request, exception):
    """
    Custom 404 die door tests wordt verwacht wanneer DEBUG=False.
    """
    return render(request, "home/404.html", status=404)


def index(request):
    return render(request, "home/index.html")
