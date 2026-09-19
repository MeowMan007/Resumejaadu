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
    from .latex_utils import latex_escape, latex_escape_url

    # Safely get personal info
    try:
        pi = resume.personal_info
    except Exception:
        pi = None

    # Format experience items with normalized bullets and date strings
    exp_list = []
    for exp in resume.experience.prefetch_related("bullets").order_by("order", "-start_date"):
        bullet_texts = [latex_escape(b.text) for b in exp.bullets.all() if b.text.strip()]
        start_str = exp.start_date.strftime("%b %Y") if exp.start_date else ""
        end_str = "Present" if exp.is_current else (exp.end_date.strftime("%b %Y") if exp.end_date else "Present")
        exp_list.append({
            "role": latex_escape(exp.role),
            "company": latex_escape(exp.company),
            "location": latex_escape(exp.location),
            "start_date": latex_escape(start_str),
            "end_date": latex_escape(end_str),
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
            "institution": latex_escape(edu.institution),
            "degree": latex_escape(edu.degree),
            "field_of_study": latex_escape(edu.field_of_study),
            "location": latex_escape(edu.location),
            "start_date": latex_escape(start_str),
            "end_date": latex_escape(end_str),
            "gpa": latex_escape(edu.gpa),
            "raw": edu,
        })

    # Format projects
    proj_list = []
    for proj in resume.projects.order_by("order"):
        clean_desc = latex_escape(proj.description) if proj.description else ""
        proj_list.append({
            "title": latex_escape(proj.name),
            "name": latex_escape(proj.name),
            "technologies": latex_escape(proj.tech_stack),
            "tech_stack": latex_escape(proj.tech_stack),
            "link": latex_escape_url(proj.link) if proj.link else "",
            "link_display": latex_escape(proj.link.replace("https://", "").replace("http://", "").rstrip("/")) if proj.link else "",
            "description": clean_desc,
            "bullets": [clean_desc] if clean_desc else [],
            "raw": proj,
        })

    # Format skill categories
    skill_cat_list = []
    all_flat_skills = []
    for cat in resume.skill_categories.order_by("order"):
        items = cat.items if isinstance(cat.items, list) else []
        escaped_items = [latex_escape(it) for it in items if it]
        all_flat_skills.extend(escaped_items)
        skill_cat_list.append({
            "name": latex_escape(cat.name),
            "category_name": latex_escape(cat.name),
            "items": escaped_items,
            "skills": escaped_items,
            "raw": cat,
        })

    # Format certifications
    cert_list = []
    for cert in resume.certifications.order_by("-date"):
        date_str = cert.date.strftime("%b %Y") if cert.date else ""
        cert_list.append({
            "name": latex_escape(cert.name),
            "issuer": latex_escape(cert.issuer),
            "date": latex_escape(date_str),
            "date_obtained": latex_escape(date_str),
            "credential_url": latex_escape_url(cert.credential_url) if cert.credential_url else "",
            "raw": cert,
        })

    full_name = latex_escape(pi.full_name) if (pi and pi.full_name) else "Firstname Lastname"
    email = pi.email if pi else ""
    phone = pi.phone if pi else ""
    location = pi.location if pi else ""
    linkedin = pi.linkedin_url if pi else ""
    github = pi.github_url if pi else ""
    website = pi.portfolio_url if pi else ""
    summary = latex_escape(pi.summary) if (pi and pi.summary) else ""

    # Build clean contact items
    contact_parts = []
    if phone:
        contact_parts.append(latex_escape(phone))
    if email:
        contact_parts.append(r"\href{mailto:" + latex_escape_url(email) + r"}{\underline{" + latex_escape(email) + r"}}")
    if linkedin:
        display_li = linkedin.replace("https://", "").replace("http://", "").rstrip("/")
        contact_parts.append(r"\href{" + latex_escape_url(linkedin) + r"}{\underline{" + latex_escape(display_li) + r"}}")
    if github:
        display_gh = github.replace("https://", "").replace("http://", "").rstrip("/")
        contact_parts.append(r"\href{" + latex_escape_url(github) + r"}{\underline{" + latex_escape(display_gh) + r"}}")
    if website:
        display_web = website.replace("https://", "").replace("http://", "").rstrip("/")
        contact_parts.append(r"\href{" + latex_escape_url(website) + r"}{\underline{" + latex_escape(display_web) + r"}}")
    if location:
        contact_parts.append(latex_escape(location))

    contact_line = " $|$ ".join(contact_parts)
    contact_line_dot = " $\\cdot$ ".join(contact_parts)

    return {
        "resume": resume,
        "personal": pi,
        "full_name": full_name,
        "email": latex_escape(email),
        "phone": latex_escape(phone),
        "location": latex_escape(location),
        "linkedin": latex_escape_url(linkedin),
        "github": latex_escape_url(github),
        "website": latex_escape_url(website),
        "portfolio": latex_escape_url(website),
        "contact_line": contact_line,
        "contact_line_dot": contact_line_dot,
        "summary": summary,
        "education": edu_list,
        "experience": exp_list,
        "projects": proj_list,
        "skill_categories": skill_cat_list,
        "skills": all_flat_skills,
        "certifications": cert_list,
        "target_role": latex_escape(resume.target_role) if resume.target_role else "",
        "e": latex_escape,
    }

