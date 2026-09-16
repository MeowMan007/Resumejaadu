"""
Management command: sync_templates

Scans resume_templates/ for manifest.json files and syncs them into the
ResumeTemplate table. Safe to run multiple times (idempotent).

Usage:
    python manage.py sync_templates
    python manage.py sync_templates --slug jake-resume
"""
import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.templates_lib.models import ResumeTemplate


class Command(BaseCommand):
    help = "Sync resume templates from resume_templates/ directory into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--slug",
            type=str,
            default=None,
            help="Only sync a specific template slug (optional).",
        )

    def handle(self, *args, **options):
        root = Path(settings.RESUME_TEMPLATE_ROOT)
        if not root.exists():
            raise CommandError(f"RESUME_TEMPLATE_ROOT does not exist: {root}")

        if options["slug"]:
            dirs = [root / options["slug"]]
        else:
            dirs = [d for d in root.iterdir() if d.is_dir()]

        created_count = updated_count = skipped_count = 0

        for template_dir in sorted(dirs):
            slug = template_dir.name
            manifest_path = template_dir / "manifest.json"

            if not manifest_path.exists():
                self.stdout.write(self.style.WARNING(f"  SKIP  {slug}: no manifest.json"))
                skipped_count += 1
                continue

            try:
                with manifest_path.open(encoding="utf-8-sig") as f:
                    data = json.load(f)
            except json.JSONDecodeError as exc:
                self.stdout.write(self.style.ERROR(f"  ERROR {slug}: invalid JSON — {exc}"))
                skipped_count += 1
                continue

            required = {"name", "source_url", "license", "engine", "category"}
            missing = required - data.keys()
            if missing:
                self.stdout.write(self.style.ERROR(f"  ERROR {slug}: missing fields {missing}"))
                skipped_count += 1
                continue

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

            if created:
                self.stdout.write(self.style.SUCCESS(f"  CREATE {slug}: {obj.name}"))
                created_count += 1
            else:
                self.stdout.write(f"  UPDATE {slug}: {obj.name}")
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. {created_count} created, {updated_count} updated, {skipped_count} skipped."
            )
        )
