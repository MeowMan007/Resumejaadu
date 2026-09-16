r"""
apps/generator/jinja_env.py

Jinja2 environment with LaTeX-safe custom delimiters.
Uses \VAR{...}, \BLOCK{...}, etc. to avoid collision with LaTeX's
native {{ }}/{% %} and % comment syntax.
"""
import pathlib
import jinja2

from django.conf import settings
from .latex_utils import latex_escape

# ─── LaTeX-safe Jinja2 Environment ──────────────────────────────────────────
def build_latex_jinja_env(template_dir: pathlib.Path) -> jinja2.Environment:
    """
    Build a Jinja2 environment configured for LaTeX template rendering.

    Delimiters chosen to be valid LaTeX (they produce no output):
      - Variable:  \\VAR{expr}
      - Block:     \\BLOCK{...} ... \\BLOCK{end...}
      - Comment:   \\#{...}
      - Line stmt: %%  (lines starting with %%)
      - Line cmt:  %#  (lines starting with %#)
    """
    env = jinja2.Environment(
        block_start_string=r"\BLOCK{",
        block_end_string="}",
        variable_start_string=r"\VAR{",
        variable_end_string="}",
        comment_start_string=r"\#{",
        comment_end_string="}",
        line_statement_prefix="%%",
        line_comment_prefix="%#",
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,
        keep_trailing_newline=True,
        loader=jinja2.FileSystemLoader(str(template_dir)),
    )

    # Register latex_escape as a filter and a global
    env.filters["latex"] = latex_escape
    env.globals["latex_escape"] = latex_escape
    env.globals["e"] = latex_escape  # shorthand: \VAR{e(value)}

    return env


def render_resume_to_tex(resume, template_obj) -> str:
    """
    Render a Resume instance + ResumeTemplate into a complete LaTeX string.

    Args:
        resume: apps.resumes.models.Resume instance (with prefetched relations)
        template_obj: apps.templates_lib.models.ResumeTemplate instance

    Returns:
        Rendered LaTeX source as a string
    """
    template_dir = template_obj.template_dir
    env = build_latex_jinja_env(template_dir)

    jinja_template = env.get_template("template.tex.jinja")

    # Build the context dict — all user strings must be escaped before
    # they reach the template, but we also expose the raw escape filter
    # so template authors can call \VAR{bullet|latex} explicitly.
    ctx = _build_context(resume)
    return jinja_template.render(**ctx)


def _build_context(resume) -> dict:
    """Build the full Jinja2 context from a Resume instance."""
    # Safely get personal info
    try:
        pi = resume.personal_info
    except Exception:
        pi = None

    return {
        "resume": resume,
        "personal": pi,
        "education": list(resume.education.order_by("order", "-start_date")),
        "experience": list(
            resume.experience.prefetch_related("bullets").order_by("order", "-start_date")
        ),
        "projects": list(resume.projects.order_by("order")),
        "skill_categories": list(resume.skill_categories.order_by("order")),
        "certifications": list(resume.certifications.order_by("-date")),
        "target_role": resume.target_role,
        # Helper: escape a value for LaTeX (usable inline in templates)
        "e": lambda v: __import__("apps.generator.latex_utils", fromlist=["latex_escape"]).latex_escape(v),
    }
