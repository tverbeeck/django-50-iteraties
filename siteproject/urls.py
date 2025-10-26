from django.contrib import admin
from django.urls import path, include

# from django.contrib.auth import views as auth_views
# from accounts.views import profile_view

from home.views import (
    dashboard_home,  # dit is voor de hoofdpagina "/"
    home_index,  # dit is voor de indexpagina "/index/"
    home_about,  # dit is voor de aboutpagina "/about/"
    profile_view,  # dit is voor de profielpagina "/accounts/profile/"
    login_view,  # dit is voor de loginpagina "/accounts/login/", net teoegevoegd op 26/10
    logout_view,  # dit is voor de logoutpagina "/accounts/logout/" en enkel de GET methode houden
)

urlpatterns = [
    # homepage / dashboard
    path("", dashboard_home, name="home"),
    # losse infopagina's
    path("index/", home_index, name="home-index"),
    path("about/", home_about, name="home-about"),
    # auth gerelateerde pagina's
    path(
        "accounts/login/",
        login_view,
        name="login",
    ),
    path(
        "accounts/logout/",
        logout_view,
        name="logout",
    ),
    path("accounts/profile/", profile_view, name="profile"),
    # notes app (met namespace 'notes', daar rekenen de tests op)
    path(
        "notes/",
        include(("notes.urls", "notes"), namespace="notes"),
    ),
    # admin site
    path("admin/", admin.site.urls),
]
