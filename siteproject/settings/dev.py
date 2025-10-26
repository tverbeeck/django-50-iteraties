# ruff: noqa: F403, F405
from .base import *

DEBUG = True  # belangrijk tijdens de ontwikkeling, anders ziet ge die generieke 500-pagina's ipv de gedetailleerde foutmeldingen
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# siteproject/settings/dev.py
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"
