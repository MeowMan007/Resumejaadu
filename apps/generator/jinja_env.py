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
    """Build the full Jinja2 context from a Resume instance with rich variable aliases."""
    from .latex_utils import latex_escape

    # Safely get personal info
    try:
        pi = resume.personal_info
    except Exception:
        pi = None

    # Format experience items with normalized bullets and date strings
    exp_list = []
    for exp in resume.experience.prefetch_related("bullets").order_by("order", "-start_date"):
        bullet_texts = [b.text for b in exp.bullets.all()]
        start_str = exp.start_date.strftime("%b %Y") if exp.start_date else ""
        end_str = "Present" if exp.is_current else (exp.end_date.strftime("%b %Y") if exp.end_date else "Present")
        exp_list.append({
            "role": exp.role,
            "company": exp.company,
            "location": exp.location,
            "start_date": start_str,
            "end_date": end_str,
            "is_current": exp.is_current,
            "bullets": bullet_texts,
            "raw": exp,
        })

    # Format education items
    edu_list = []
    for edu in resume.education.order_by("order", "-start_date"):
        start_str = edu.start_date.strftime("%b %Y") if edu.start_date else ""
        end_str = "Present" if edu.is_current else (edu.end_date.strftime("%b %Y") if edu.end_date else "")
        edu_list.append({
            "institution": edu.institution,
            "degree": edu.degree,
            "field_of_study": edu.field_of_study,
            "location": edu.location,
            "start_date": start_str,
            "end_date": end_str,
            "gpa": edu.gpa,
            "raw": edu,
        })

    # Format projects
    proj_list = []
    for proj in resume.projects.order_by("order"):
        proj_list.append({
            "title": proj.name,
            "name": proj.name,
            "technologies": proj.tech_stack,
            "tech_stack": proj.tech_stack,
            "link": proj.link,
            "description": proj.description,
            "bullets": [proj.description] if proj.description else [],
            "raw": proj,
        })

    # Format skill categories
    skill_cat_list = []
    all_flat_skills = []
    for cat in resume.skill_categories.order_by("order"):
        items = cat.items if isinstance(cat.items, list) else []
        all_flat_skills.extend(items)
        skill_cat_list.append({
            "name": cat.name,
            "category_name": cat.name,
            "items": items,
            "skills": items,
            "raw": cat,
        })

    # Format certifications
    cert_list = []
    for cert in resume.certifications.order_by("-date"):
        date_str = cert.date.strftime("%b %Y") if cert.date else ""
        cert_list.append({
            "name": cert.name,
            "issuer": cert.issuer,
            "date": date_str,
            "date_obtained": date_str,
            "credential_url": cert.credential_url,
            "raw": cert,
        })

    full_name = pi.full_name if pi else "Firstname Lastname"
    email = pi.email if pi else ""
    phone = pi.phone if pi else ""
    location = pi.location if pi else ""
    linkedin = pi.linkedin_url if pi else ""
    github = pi.github_url if pi else ""
    website = pi.portfolio_url if pi else ""
    summary = pi.summary if pi else ""

    return {
        "resume": resume,
        "personal": pi,
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "location": location,
        "linkedin": linkedin,
        "github": github,
        "website": website,
        "portfolio": website,
        "summary": summary,
        "education": edu_list,
        "experience": exp_list,
        "projects": proj_list,
        "skill_categories": skill_cat_list,
        "skills": all_flat_skills,
        "certifications": cert_list,
        "target_role": resume.target_role,
        "e": latex_escape,
    }

