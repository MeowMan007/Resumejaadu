"""config/settings/dev.py — Local development settings."""
from .base import *  # noqa: F401, F403

DEBUG = True

INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405

MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa: F405

INTERNAL_IPS = ["127.0.0.1"]

# Use SQLite for local dev if no DATABASE_URL is set
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

# Simpler static files for dev
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Email to console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Celery — run tasks eagerly in dev (no worker needed)
CELERY_TASK_ALWAYS_EAGER = False  # Set True to skip Celery entirely in dev
