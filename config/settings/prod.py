"""config/settings/prod.py — Production settings."""
from .base import *  # noqa: F401, F403

import os
import environ

DEBUG = False

# Security & Reverse Proxy headers (critical for Vercel edge/CDN)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Allowed hosts (support Vercel preview & production URLs automatically)
allowed_hosts_env = os.getenv("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [
    ".vercel.app",
    ".now.sh",
    "localhost",
    "127.0.0.1",
] + [h.strip() for h in allowed_hosts_env.split(",") if h.strip()]

# CSRF Trusted Origins (required for POST forms on Vercel)
csrf_origins_env = os.getenv("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [
    "https://*.vercel.app",
    "https://*.now.sh",
] + [o.strip() for o in csrf_origins_env.split(",") if o.strip()]

# Database: PostgreSQL (Neon / Supabase / Railway / Vercel Postgres)
env_prod = environ.Env()
db_default = "sqlite:////tmp/db.sqlite3" if os.getenv("VERCEL") else f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
DATABASES = {"default": env_prod.db("DATABASE_URL", default=db_default)}
if DATABASES["default"]["ENGINE"] != "django.db.backends.sqlite3":
    DATABASES["default"]["CONN_MAX_AGE"] = 60

# Media & Storage Configuration
if os.getenv("USE_S3", "False") == "True":
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "us-east-1")
    AWS_DEFAULT_ACL = "private"
    AWS_S3_FILE_OVERWRITE = False
    MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/"
elif os.getenv("VERCEL"):
    # On Vercel serverless functions, only /tmp is writable
    from pathlib import Path
    MEDIA_ROOT = Path("/tmp/media")
