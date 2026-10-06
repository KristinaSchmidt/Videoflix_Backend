"""
Django settings for the Videoflix backend.

Central configuration for Django, PostgreSQL, Redis, authentication,
email, CORS, static files and media files.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "unsafe-development-key",
)

DEBUG = os.getenv(
    "DEBUG",
    "False",
).lower() == "true"

ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS",
    "localhost",
).split(",")

CSRF_TRUSTED_ORIGINS = os.environ.get(
    "CSRF_TRUSTED_ORIGINS",
    "http://localhost:5500",
).split(",")


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "django_rq",

    "users",
    "videos",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "core.urls"


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


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get(
            "DB_NAME",
            "videoflix_db",
        ),
        "USER": os.environ.get(
            "DB_USER",
            "videoflix_user",
        ),
        "PASSWORD": os.environ.get(
            "DB_PASSWORD",
            "supersecretpassword",
        ),
        "HOST": os.environ.get(
            "DB_HOST",
            "db",
        ),
        "PORT": os.environ.get(
            "DB_PORT",
            "5432",
        ),
    }
}


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


LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)


AUTH_USER_MODEL = "users.User"


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "users.authentication.CookieJWTAuthentication",
    ],
}


MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
        "OPTIONS": {
            "host": os.getenv(
                "EMAIL_HOST",
                "smtp.example.com",
            ),
            "port": int(
                os.getenv(
                    "EMAIL_PORT",
                    "587",
                )
            ),
            "username": os.getenv(
                "EMAIL_HOST_USER",
                "",
            ),
            "password": os.getenv(
                "EMAIL_HOST_PASSWORD",
                "",
            ),
            "use_tls": os.getenv(
                "EMAIL_USE_TLS",
                "True",
            ).lower() == "true",
            "use_ssl": os.getenv(
                "EMAIL_USE_SSL",
                "False",
            ).lower() == "true",
        },
    }
}


DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    os.getenv(
        "EMAIL_HOST_USER",
        "noreply@videoflix.local",
    ),
)


FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://127.0.0.1:5500",
)


CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]

CORS_ALLOW_CREDENTIALS = True


REDIS_HOST = os.environ.get(
    "REDIS_HOST",
    "redis",
)

REDIS_PORT = int(
    os.environ.get(
        "REDIS_PORT",
        "6379",
    )
)

REDIS_DB = int(
    os.environ.get(
        "REDIS_DB",
        "0",
    )
)


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get(
            "REDIS_LOCATION",
            "redis://redis:6379/1",
        ),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "videoflix",
    }
}


RQ_QUEUES = {
    "default": {
        "HOST": REDIS_HOST,
        "PORT": REDIS_PORT,
        "DB": REDIS_DB,
        "DEFAULT_TIMEOUT": 900,
        "REDIS_CLIENT_KWARGS": {},
    },
}