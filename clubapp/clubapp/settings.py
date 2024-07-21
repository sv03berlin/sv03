"""
Django settings for clubapp project.

Generated by 'django-admin startproject' using Django 4.0.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
from os import environ
from pathlib import Path

import django_stubs_ext
import sentry_sdk
from django.contrib.messages import constants as messages
from dotenv import load_dotenv

django_stubs_ext.monkeypatch()

sentry_sdk.init(
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)


BASE_DIR = Path(__file__).resolve().parent.parent

ENV_FILE = BASE_DIR.parent / ".env"
load_dotenv(ENV_FILE)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

STATIC_ROOT = "/clubapp_static/"

ENABLE_OIDC_LOGIN = os.environ.get("ENABLE_OIDC_LOGIN", "False").lower() == "true"
ENABLE_DJANGO_LOGIN = os.environ.get("ENABLE_DJANGO_LOGIN", "True").lower() == "true"

if not ENABLE_OIDC_LOGIN and not ENABLE_DJANGO_LOGIN:
    msg = "ENABLE_OIDC_LOGIN and ENABLE_DJANGO_LOGIN cannot be both False"
    raise ValueError(msg)
VIRTUAL_HOST = os.environ.get("VIRTUAL_HOST", "localhost:8000").removesuffix("/")


# Application definition

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "mozilla_django_oidc",
    "crispy_forms",
    "django_filters",
    "crispy_bootstrap5",
    "clubapp.refundflow",
    "clubapp.club",
    "clubapp.clubwork",
    "clubapp.reservationflow",
    "django_extensions",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "mozilla_django_oidc.middleware.SessionRefresh",
]

AUTHENTICATION_BACKENDS = []
if ENABLE_OIDC_LOGIN:
    AUTHENTICATION_BACKENDS.append("clubapp.clubapp.oidc.ClubOIDCAuthenticationBackend")
if ENABLE_DJANGO_LOGIN:
    AUTHENTICATION_BACKENDS.append("django.contrib.auth.backends.ModelBackend")

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 60 * 60 * 24  # 24 hours

ROOT_URLCONF = "clubapp.clubapp.urls"

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
                "clubapp.clubapp.context_processors.club_processor",
            ],
        },
    },
]

WSGI_APPLICATION = "clubapp.clubapp.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

MEDIA_ROOT = Path("./clubapp_data/")
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": MEDIA_ROOT / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "club.User"


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "de-DE"

TIME_ZONE = "CET"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "/static/"

# Additional locations of static files
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_REDIRECT_URL = "/"

if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "")

CLUB_NAME = os.environ.get("CLUB_NAME", "Club")
CLUB_NAME_SHORT = os.environ.get("CLUB_NAME_SHORT", "CN")
CLUB_IMPRINT = os.environ.get("CLUB_IMPRINT", "#")
THIS_APP_NAME = os.environ.get("THIS_APP_NAME", "Clubapp")

STAGING = os.environ.get("STAGING", "False").lower() == "true"

INDEX_IS_LOGIN = os.environ.get("INDEX_IS_LOGIN", "True").lower() == "true"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

MESSAGE_TAGS = {
    messages.DEBUG: "alert-info",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# OIDC
OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS = 60 * 60 * 24  # 24 hours
OIDC_RP_SIGN_ALGO = "RS256"
# OIDC_USERNAME_ALGO ""
OIDC_RP_SCOPES = "openid email profile roles"

OIDC_RP_CLIENT_ID = environ.get("OIDC_RP_CLIENT_ID", "")
OIDC_RP_CLIENT_SECRET = environ.get("OIDC_RP_CLIENT_SECRET")

OIDC_OP_AUTHORIZATION_ENDPOINT = environ.get("OIDC_OP_AUTHORIZATION_ENDPOINT")
OIDC_OP_TOKEN_ENDPOINT = environ.get("OIDC_OP_TOKEN_ENDPOINT")
OIDC_OP_USER_ENDPOINT = environ.get("OIDC_OP_USER_ENDPOINT")
OIDC_OP_JWKS_ENDPOINT = environ.get("OIDC_OP_JWKS_ENDPOINT")
OIDC_OP_LOGOUT_ENDPOINT = environ.get("OIDC_OP_LOGOUT_ENDPOINT", "")
OIDC_OP_LOGOUT_URL_METHOD = "clubapp.clubapp.oidc.provider_logout"
ALLOW_LOGOUT_GET_METHOD = True

KEYCLOAK_ACCOUNT_URL = environ.get("KEYCLOAK_ACCOUNT_URL", "")

# logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(name)s] %(levelprefix)s %(message)s",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.environ.get("LOG_LEVEL", "INFO"),
    },
}
