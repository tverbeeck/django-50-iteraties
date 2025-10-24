"""
Basissettings, gedeeld door dev en prod.
Leest optioneel variabelen uit .env via python-dotenv.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Laad .env (alleen als bestand bestaat)
BASE_DIR = Path(__file__).resolve().parents[2]  # .../Django
load_dotenv(BASE_DIR / ".env")

# Kern
SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-key-change-me")
DEBUG = False  # override in dev.py

ALLOWED_HOSTS = (
    os.getenv("ALLOWED_HOSTS", "").split(",") if os.getenv("ALLOWED_HOSTS") else []
)

# Apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # project apps
    "home",
    "notes",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "siteproject.urls"
WSGI_APPLICATION = "siteproject.wsgi.application"
ASGI_APPLICATION = "siteproject.asgi.application"

# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "siteproject.context_processors.site_meta",
            ],
        },
    },
]

# DB (SQLite default), override via DATABASE_URL in prod
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Locale
LANGUAGE_CODE = "nl"
TIME_ZONE = "Europe/Brussels"
USE_I18N = True
USE_TZ = True

# Static
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"  # gebruikt in prod collectstatic

# Security sensible defaults (verder aangescherpt in prod)
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
