from django.contrib import admin
from django.urls import path, include
from home import views as home_views

# Gebruik onze eigen 404-pagina als DEBUG=False in tests
handler404 = "home.views.custom_404"

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # Dashboard / startpagina
    # reverse("home") moet werken
    path("", home_views.home, name="home"),
    # Klassieke index-url
    # reverse("home-index") moet werken
    path("index/", home_views.home, name="home-index"),
    # About-pagina
    # reverse("home-about") moet werken
    path("about/", home_views.about, name="home-about"),
    # Notes (CRUD + filters + public wiki + API)
    # reverse("notes:...") moet werken
    path(
        "notes/",
        include(("notes.urls", "notes"), namespace="notes"),
    ),
]
