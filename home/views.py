from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.urls import reverse

from notes.models import Note, Tag


@require_GET
def dashboard_home(request):
    """
    Dashboard op "/":
    - recente notities
    - lijst van tags
    """
    recent_notes = Note.objects.all().order_by("-updated_at", "-created_at", "title")[
        :5
    ]
    tags = Tag.objects.order_by("name")

    return render(
        request,
        "home/dashboard.html",
        {
            "recent_notes": recent_notes,
            "tags": tags,
        },
    )


@require_GET
def home_index(request):
    """Eenvoudige pagina op /index/."""
    return render(request, "home/index.html")


@require_GET
def home_about(request):
    """Eenvoudige pagina op /about/."""
    return render(request, "home/about.html")


@login_required
def profile_view(request):
    """Profielpagina alleen zichtbaar als je ingelogd bent."""
    return render(
        request,
        "accounts/profile.html",
        {
            "user": request.user,
        },
    )


@require_GET
def logout_view(request):
    """
    Uitloggen via GET.
    In productie zou je meestal POST afdwingen, maar voor dit project (en de navbar-link)
    houden we GET toe.
    """
    logout(request)
    return redirect("home")


def login_view(request):
    """
    Eenvoudige login view:
    - GET: toon formulier
    - POST: probeer in te loggen
    - bij succes: stuur naar ?next=... of naar dashboard
    """
    error = None

    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)

            # respecteer ?next=/... als die aanwezig is
            next_url = request.GET.get("next") or reverse("home")
            return redirect(next_url)
        else:
            error = "Login mislukt. Controleer je gebruikersnaam en wachtwoord."

    return render(
        request,
        "accounts/login.html",
        {
            "error": error,
        },
    )
