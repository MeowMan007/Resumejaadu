# Deploying ResumeJaadu on Vercel

ResumeJaadu is fully configured for zero-configuration serverless deployment on **Vercel** with Django 5.1 and Python 3.12.

---

## Architecture on Vercel

- **Web Frontend & API**: Runs as a serverless Vercel Function (Fluid compute) via `config.wsgi:application` (`config/wsgi.py`).
- **Static Assets**: Handled automatically via `WhiteNoise` and distributed globally through the **Vercel CDN**.
- **Database**: Connects to any hosted PostgreSQL database (e.g., [Neon](https://neon.tech), [Supabase](https://supabase.com), [Railway](https://railway.app), or Vercel Postgres) via `DATABASE_URL`.
- **LaTeX Compilation (Worker)**: PDF rendering requires a TeX Live environment (`Dockerfile.worker`), which runs independently on container platforms like Railway, Render, Fly.io, or Docker Compose with shared Redis & PostgreSQL.

---

## 1. Quick Deploy Steps

1. **Push your repository** to GitHub, GitLab, or Bitbucket.
2. Go to [vercel.com/new](https://vercel.com/new) and **import your repository**.
3. Vercel automatically detects the **Django** framework, locates `manage.py`, and sets the WSGI entrypoint (`config/wsgi.py`).
4. Add the required **Environment Variables** (see below) in the Vercel project settings.
5. Click **Deploy**.

---

## 2. Environment Variables

Configure these in **Project Settings → Environment Variables**:

| Variable | Required | Description | Example |
|---|---|---|---|
| `SECRET_KEY` | **Yes** | Django secret key | `django-insecure-...` |
| `DATABASE_URL` | **Yes** | PostgreSQL connection URL | `postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require` |
| `GROQ_API_KEY` | Recommended | Groq API key for AI assistant | `gsk_...` |
| `ALLOWED_HOSTS` | Optional | Custom domains (comma-separated; `.vercel.app` included automatically) | `myresume.com,app.myresume.com` |
| `CSRF_TRUSTED_ORIGINS` | Optional | Custom origin URLs (comma-separated; `https://*.vercel.app` included automatically) | `https://myresume.com` |
| `CELERY_BROKER_URL` | Optional | Redis URL for Celery async PDF tasks (e.g., Upstash Redis) | `rediss://default:xxx@...upstash.io:6379` |
| `USE_S3` | Optional | Set to `True` if storing generated PDFs / user uploads in AWS S3 | `True` |
| `AWS_STORAGE_BUCKET_NAME` | Optional | AWS S3 Bucket Name | `my-resume-bucket` |
| `AWS_ACCESS_KEY_ID` | Optional | AWS Access Key | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | Optional | AWS Secret Key | `...` |

---

## 3. Database Migrations & Initial Setup

Since Vercel serverless builds are ephemeral, run initial migrations and template sync from your local machine connected to your production database:

```bash
# Option A: With Vercel CLI
vercel pull --environment=production
python manage.py migrate
python manage.py sync_templates

# Option B: Direct DATABASE_URL
$env:DATABASE_URL="postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require"
python manage.py migrate --settings=config.settings.prod
python manage.py sync_templates --settings=config.settings.prod
```

---

## 4. Key Configuration Files Included

- **`vercel.json`**: Configures function memory (1024MB) and maximum execution duration (60s).
- **`pyproject.toml`**: Explicitly defines `[tool.vercel] entrypoint = "config.wsgi:application"`.
- **`config/wsgi.py`**: Exposes both `application` and `app` for Vercel WSGI resolution.
- **`config/settings/prod.py`**:
  - Automatically whitelists `.vercel.app` in `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`.
  - Configures `SECURE_PROXY_SSL_HEADER` for Vercel edge/CDN SSL termination.
  - Safe database fallback prevents build-time failures.
  - WhiteNoise static asset serving with non-strict manifest.
