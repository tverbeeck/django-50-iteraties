# ruff: noqa: F403, F405
from .base import *
import os
import dj_database_url

DEBUG = False

# Vereist in prod — bijv. domein of render.com/railway host
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "example.com").split(",")

# Database via DATABASE_URL (postgres://... of mysql://...), fallback naar sqlite
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DATABASES["default"] = dj_database_url.parse(DATABASE_URL, conn_max_age=600)

# Security aanscherpen
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "true").lower() == "true"
