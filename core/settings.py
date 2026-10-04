"""
Django settings for the Videoflix backend.

This module contains the central configuration for installed applications,
middleware, authentication, database access, email, CORS and media files.
"""

from pathlib import Path


# Base directory of the Django project.
BASE_DIR = Path(__file__).resolve().parent.parent


# Development configuration.
SECRET_KEY = "django-insecure-lo!6n==3b^1=-jzr63e=cd_d=p3^saqx-1gl&p-_@p0*h@4^7)"

DEBUG = True

ALLOWED_HOSTS = []


# Applications used by the project.
INSTALLED_APPS = [
    # Django applications
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party applications
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "django_rq",

    # Local applications
    "users",
    "videos",
]


# Middleware configuration.
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "core.urls"


# Template configuration.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "core.wsgi.application"


# Database configuration.
# SQLite is used during local development.
# PostgreSQL configuration will be added with Docker later.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation.
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# Internationalization.
LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files.
STATIC_URL = "static/"


# Custom user model.
AUTH_USER_MODEL = "users.User"


# Django REST Framework configuration.
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "users.authentication.CookieJWTAuthentication",
    ],
}


# Email configuration for local development.
# Emails are printed to the terminal instead of being sent.
MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.console.EmailBackend",
    }
}

DEFAULT_FROM_EMAIL = "noreply@videoflix.local"


# Frontend address used for activation and password reset links.
FRONTEND_URL = "http://127.0.0.1:5500"


# CORS configuration.
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]

CORS_ALLOW_CREDENTIALS = True


# Media configuration for uploaded videos and thumbnails.
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"