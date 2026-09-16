"""
apps/generator/tasks.py — Celery tasks for PDF generation.
"""
import logging
import pathlib
import tempfile

from celery import shared_task
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name="generator.generate_resume_pdf",
    queue="pdf_generation",
    max_retries=2,
    default_retry_delay=10,
    time_limit=120,
    soft_time_limit=90,
)
def generate_resume_pdf(self, generated_pdf_id: int) -> dict:
    """
    Celery task: Render Resume → LaTeX → PDF, store result, generate thumbnail.

    Args:
        generated_pdf_id: pk of a GeneratedPDF instance (status="pending")

    Returns:
        dict with 'status' and 'pdf_url' or 'error'
    """
    from apps.resumes.models import GeneratedPDF
    from apps.generator.jinja_env import render_resume_to_tex
    from apps.generator.compiler import compile_tex_to_pdf, generate_thumbnail, LatexCompileError

    try:
        gen = GeneratedPDF.objects.select_related(
            "resume__personal_info",
            "resume__template",
            "template",
        ).prefetch_related(
            "resume__education",
            "resume__experience__bullets",
            "resume__projects",
            "resume__skill_categories",
            "resume__certifications",
        ).get(pk=generated_pdf_id)
    except GeneratedPDF.DoesNotExist:
        logger.error(f"GeneratedPDF #{generated_pdf_id} not found")
        return {"status": "failed", "error": "Record not found"}

    # Mark as compiling
    gen.status = "compiling"
    gen.celery_task_id = self.request.id or ""
    gen.save(update_fields=["status", "celery_task_id"])

    try:
        # 1. Render Jinja2 → LaTeX source
        logger.info(f"Rendering LaTeX for GeneratedPDF #{generated_pdf_id}")
        tex_source = render_resume_to_tex(gen.resume, gen.template)

        # 2. Compile LaTeX → PDF (sandboxed)
        logger.info(f"Compiling with {gen.template.engine}")
        pdf_path = compile_tex_to_pdf(
            tex_source=tex_source,
            engine=gen.template.engine,
            asset_dir=gen.template.template_dir,
        )

        # 3. Save PDF to Django storage
        pdf_filename = f"resume_{gen.resume_id}_{gen.template.slug}.pdf"
        with open(pdf_path, "rb") as f:
            gen.file.save(pdf_filename, ContentFile(f.read()), save=False)

        # 4. Generate thumbnail before cleaning up temp PDF
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_thumb:
            thumb_path = pathlib.Path(tmp_thumb.name)

        try:
            thumb_ok = generate_thumbnail(pdf_path, thumb_path)
            if thumb_ok and thumb_path.exists():
                thumb_filename = f"thumb_{gen.resume_id}_{gen.template.slug}.png"
                with open(thumb_path, "rb") as tf:
                    gen.thumbnail.save(thumb_filename, ContentFile(tf.read()), save=False)
        finally:
            # Clean up temp files
            try:
                pdf_path.unlink()
            except OSError:
                pass
            try:
                thumb_path.unlink()
            except OSError:
                pass

        gen.status = "success"
        gen.compile_log_excerpt = ""
        gen.save(update_fields=["file", "thumbnail", "status", "compile_log_excerpt"])

        logger.info(f"PDF #{generated_pdf_id} compiled successfully")
        return {
            "status": "success",
            "pdf_url": gen.file.url if gen.file else None,
        }

    except Exception as exc:
        log_excerpt = getattr(exc, "log_excerpt", str(exc))
        logger.error(f"PDF #{generated_pdf_id} failed: {log_excerpt}")

        gen.status = "failed"
        gen.compile_log_excerpt = str(log_excerpt)[:3000]
        gen.save(update_fields=["status", "compile_log_excerpt"])

        # Retry on transient errors (not compile errors)
        from apps.generator.compiler import LatexCompileError
        if not isinstance(exc, LatexCompileError):
            raise self.retry(exc=exc)

        return {"status": "failed", "error": "LaTeX compilation failed"}
