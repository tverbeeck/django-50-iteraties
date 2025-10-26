# home/urls.py
from django.urls import path
from .views import HomeDashboardView, HomeIndexView, AboutView

urlpatterns = [
    path("", HomeDashboardView.as_view(), name="home"),
    path("index/", HomeIndexView.as_view(), name="home-index"),
    path("about/", AboutView.as_view(), name="home-about"),
]
