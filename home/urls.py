# home/urls.py
from django.urls import include, path
from . import views

app_name = "home"  # <-- dit voegt de namespace 'home' toe

urlpatterns = [
    path("", views.home, name="home"),  # naam 'home:home'
    path("about/", views.about, name="about"),  # naam 'home:about'
    path("", include("home.urls", namespace="home")),
]
