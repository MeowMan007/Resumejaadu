"""
apps/generator/latex_utils.py

LaTeX input sanitisation — applied to EVERY user-supplied string before
it is injected into a template.  Failure to do this allows users to inject
arbitrary LaTeX or shell commands (via \\write18 etc.).

Injection payloads tested against in tests/test_latex_escape.py.
"""
import re


# ─── Characters that have special meaning in LaTeX ───────────────────────────
# Order matters: the backslash replacement must come FIRST, otherwise
# the backslashes we insert for other replacements would themselves get escaped.
_REPLACEMENTS = [
    ("\\", r"\textbackslash{}"),   # MUST be first
    ("{",  r"\{"),
    ("}",  r"\}"),
    ("$",  r"\$"),
    ("&",  r"\&"),
    ("#",  r"\#"),
    ("_",  r"\_"),
    ("%",  r"\%"),
    ("~",  r"\textasciitilde{}"),
    ("^",  r"\textasciicircum{}"),
]


def latex_escape(value) -> str:
    """
    Escape a Python value for safe inclusion in a LaTeX document.

    - None / falsy values return an empty string.
    - Applies a minimal, ordered set of character substitutions.
    - Does NOT strip HTML tags — the app should never store raw HTML in resume fields.

    Usage in Jinja2 templates:
        \\VAR{personal.full_name|latex}
        \\VAR{bullet.text|latex}
    """
    if value is None:
        return ""
    out = str(value)
    for char, replacement in _REPLACEMENTS:
        out = out.replace(char, replacement)
    return out


def latex_escape_url(url: str) -> str:
    """
    Escape a URL for LaTeX's \\href{}{} command.
    URLs only need % escaped (not the full set, as the other chars are valid in URLs).
    We wrap with \\url{} so hyperref handles the rest.
    """
    if not url:
        return ""
    # Only escape % in URLs
    return url.replace("%", r"\%")


def format_date_latex(date_obj, fmt="%b %Y") -> str:
    """
    Format a Python date/datetime object as a LaTeX-safe string.
    Returns empty string for None.
    """
    if date_obj is None:
        return ""
    return date_obj.strftime(fmt)


def sanitize_filename(name: str) -> str:
    """
    Convert a string to a safe filename (for generated PDFs).
    """
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[\s-]+", "_", name)
    return name[:100]
