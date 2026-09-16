"""
apps/templates_lib/models.py — Resume Template catalog model.
"""
from django.db import models


class ResumeTemplate(models.Model):
    ENGINE_CHOICES = [
        ("pdflatex", "pdfLaTeX"),
        ("xelatex", "XeLaTeX"),
        ("lualatex", "LuaLaTeX"),
    ]
    CATEGORY_CHOICES = [
        ("single_column", "Single Column"),
        ("two_column", "Two Column / Sidebar"),
        ("academic", "Academic / CV"),
        ("creative", "Creative / Colorful"),
    ]

    slug = models.SlugField(unique=True, help_text="Matches the folder name in resume_templates/")
    name = models.CharField(max_length=120)
    source_url = models.URLField(help_text="Original Overleaf or GitHub URL")
    license = models.CharField(max_length=80, help_text="e.g. LPPL 1.3c, MIT, CC BY 4.0")
    engine = models.CharField(max_length=10, choices=ENGINE_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    supports_photo = models.BooleanField(default=False)
    supports_projects = models.BooleanField(default=True)
    supports_certifications = models.BooleanField(default=True)
    is_one_page_design = models.BooleanField(default=True)
    ats_friendly = models.BooleanField(
        default=False,
        help_text="True if template is designed for ATS parsing (minimal graphics/tables)"
    )

    thumbnail = models.ImageField(
        upload_to="template_thumbnails/",
        null=True,
        blank=True,
        help_text="Auto-generated from compiled sample or manually uploaded"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Resume Template"
        verbose_name_plural = "Resume Templates"

    def __str__(self):
        return f"{self.name} ({self.get_engine_display()})"

    @property
    def template_dir(self):
        """Absolute path to this template's folder."""
        from django.conf import settings
        return settings.RESUME_TEMPLATE_ROOT / self.slug

    @property
    def jinja_template_path(self):
        return self.template_dir / "template.tex.jinja"
