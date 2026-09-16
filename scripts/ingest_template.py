#!/usr/bin/env python
"""
scripts/ingest_template.py

Usage:
    python scripts/ingest_template.py <slug>

Reads resume_templates/<slug>/manifest.json and upserts a ResumeTemplate
record in the database. Call after dropping your .tex.jinja file in the
correct folder.

Example:
    python scripts/ingest_template.py jake-resume
"""
import json
import os
import sys
import django

# ── Bootstrap Django ────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

from pathlib import Path
from django.conf import settings
from apps.templates_lib.models import ResumeTemplate


def ingest(slug: str):
    template_dir = Path(settings.RESUME_TEMPLATE_ROOT) / slug
    manifest_path = template_dir / "manifest.json"

    if not manifest_path.exists():
        print(f"[ERROR] manifest.json not found at {manifest_path}", file=sys.stderr)
        sys.exit(1)

    with manifest_path.open() as f:
        data = json.load(f)

    required = {"name", "source_url", "license", "engine", "category"}
    missing = required - data.keys()
    if missing:
        print(f"[ERROR] manifest.json is missing fields: {missing}", file=sys.stderr)
        sys.exit(1)

    obj, created = ResumeTemplate.objects.update_or_create(
        slug=slug,
        defaults={
            "name": data["name"],
            "source_url": data["source_url"],
            "license": data["license"],
            "engine": data["engine"],
            "category": data["category"],
            "supports_photo": data.get("supports_photo", False),
            "supports_projects": data.get("supports_projects", True),
            "supports_certifications": data.get("supports_certifications", True),
            "is_one_page_design": data.get("is_one_page_design", True),
            "ats_friendly": data.get("ats_friendly", False),
            "is_active": data.get("is_active", True),
        },
    )

    action = "Created" if created else "Updated"
    print(f"[OK] {action} template: {obj.name} (slug={slug})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/ingest_template.py <slug>")
        sys.exit(1)
    ingest(sys.argv[1])
