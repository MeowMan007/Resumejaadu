#!/usr/bin/env python
"""
scripts/compile_all_templates_smoke_test.py

Smoke-tests every active template by rendering a minimal resume context
and running pdflatex on it. Requires TeX Live to be installed.

Usage:
    python scripts/compile_all_templates_smoke_test.py

Exit code 0 = all pass, non-zero = one or more failures.
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

from apps.templates_lib.models import ResumeTemplate
from apps.generator.jinja_env import build_latex_jinja_env
from apps.generator.compiler import compile_tex_to_pdf
import tempfile, pathlib, traceback

SAMPLE_CONTEXT = {
    "full_name": "Jane Doe",
    "email": "jane@example.com",
    "phone": "+1 555 0100",
    "location": "San Francisco, CA",
    "linkedin_url": "https://linkedin.com/in/janedoe",
    "github_url": "https://github.com/janedoe",
    "portfolio_url": "https://janedoe.dev",
    "summary": "Results-driven software engineer with 5 years of experience.",
    "experience": [
        {
            "company": "Acme Corp",
            "role": "Software Engineer",
            "location": "Remote",
            "start_date": "2020-01",
            "end_date": "Present",
            "bullets": ["Built microservices with Django & Celery.", "Reduced API latency by 40%."],
        }
    ],
    "education": [
        {
            "institution": "MIT",
            "degree": "B.S. Computer Science",
            "field_of_study": "Computer Science",
            "location": "Cambridge, MA",
            "start_date": "2015-09",
            "end_date": "2019-05",
            "gpa": "3.9/4.0",
        }
    ],
    "skills": [
        {"name": "Languages", "items": ["Python", "Go", "TypeScript"]},
        {"name": "Frameworks", "items": ["Django", "FastAPI", "React"]},
    ],
    "projects": [
        {
            "name": "ResumeJaadu",
            "tech_stack": "Django, LaTeX, Celery, Redis",
            "link": "https://github.com/MeowMan007/Resumejaadu",
            "description": "AI-powered resume builder with 20 LaTeX templates.",
        }
    ],
    "certifications": [
        {"name": "AWS Solutions Architect", "issuer": "Amazon", "date": "2023-06", "credential_url": ""},
    ],
    "photo_path": None,
}


def run_smoke_tests():
    templates = list(ResumeTemplate.objects.filter(is_active=True))
    if not templates:
        print("[WARN] No active templates found in database. Run sync_templates first.")
        return 0

    passed, failed = [], []

    for tmpl in templates:
        print(f"  Testing: {tmpl.name} ({tmpl.slug})...", end=" ", flush=True)
        try:
            jinja_env = build_latex_jinja_env(tmpl.template_dir)
            tex_source = jinja_env.get_template("template.tex.jinja").render(SAMPLE_CONTEXT)

            with tempfile.TemporaryDirectory() as tmpdir:
                tex_file = pathlib.Path(tmpdir) / "resume.tex"
                tex_file.write_text(tex_source, encoding="utf-8")
                pdf_bytes, log = compile_tex_to_pdf(tex_file, engine=tmpl.engine)

            if pdf_bytes and len(pdf_bytes) > 1000:
                print("PASS ✅")
                passed.append(tmpl.slug)
            else:
                print("FAIL ❌ (empty PDF)")
                failed.append(tmpl.slug)
        except Exception:
            print("FAIL ❌")
            traceback.print_exc()
            failed.append(tmpl.slug)

    print(f"\n{'─'*50}")
    print(f"Results: {len(passed)} passed, {len(failed)} failed")
    if failed:
        print(f"Failed slugs: {', '.join(failed)}")
    return len(failed)


if __name__ == "__main__":
    sys.exit(run_smoke_tests())
