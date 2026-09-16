"""
apps/resumes/models.py — Core resume data models.
All models as specified in §5 of the build spec.
"""
from django.conf import settings
from django.db import models


class Resume(models.Model):
    STATUS_CHOICES = [("draft", "Draft"), ("final", "Final")]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resumes",
    )
    title = models.CharField(max_length=120, default="Untitled Resume")
    template = models.ForeignKey(
        "templates_lib.ResumeTemplate",
        on_delete=models.PROTECT,
        related_name="resumes",
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    target_role = models.CharField(
        max_length=120,
        blank=True,
        help_text="Used to focus AI enhancements",
    )
    # Wizard step tracking (0–8)
    current_step = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Resume"
        verbose_name_plural = "Resumes"

    def __str__(self):
        return f"{self.title} — {self.user.email}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("resumes:wizard_step", kwargs={"pk": self.pk, "step": "personal-info"})

    @property
    def latest_pdf(self):
        return self.generated_pdfs.order_by("-created_at").first()


class PersonalInfo(models.Model):
    resume = models.OneToOneField(
        Resume, on_delete=models.CASCADE, related_name="personal_info"
    )
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    location = models.CharField(max_length=120, blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    summary = models.TextField(
        blank=True,
        help_text="Professional summary / objective. AI-enhanced field.",
    )
    photo = models.ImageField(
        upload_to="resume_photos/",
        blank=True,
        null=True,
        help_text="Optional headshot. Max 5MB. JPEG/PNG/WebP only.",
    )

    def __str__(self):
        return f"PersonalInfo for Resume #{self.resume_id}"


class Education(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="education")
    institution = models.CharField(max_length=160)
    degree = models.CharField(max_length=160)
    field_of_study = models.CharField(max_length=160, blank=True)
    location = models.CharField(max_length=120, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    gpa = models.CharField(max_length=20, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "-start_date"]
        verbose_name = "Education"
        verbose_name_plural = "Education"

    def __str__(self):
        return f"{self.degree} at {self.institution}"


class Experience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="experience")
    company = models.CharField(max_length=160)
    role = models.CharField(max_length=160)
    location = models.CharField(max_length=120, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "-start_date"]
        verbose_name = "Experience"
        verbose_name_plural = "Experiences"

    def __str__(self):
        return f"{self.role} at {self.company}"


class ExperienceBullet(models.Model):
    experience = models.ForeignKey(
        Experience, on_delete=models.CASCADE, related_name="bullets"
    )
    text = models.TextField(help_text="Single bullet point. AI-enhanced field.")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.text[:80]


class Project(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="projects")
    name = models.CharField(max_length=160)
    tech_stack = models.CharField(max_length=200, blank=True)
    link = models.URLField(blank=True)
    description = models.TextField(blank=True, help_text="AI-enhanced field.")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


class SkillCategory(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="skill_categories")
    name = models.CharField(max_length=80, help_text="e.g. Languages, Frameworks, Tools")
    items = models.JSONField(default=list, help_text="List of skill strings")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Skill Category"
        verbose_name_plural = "Skill Categories"

    def __str__(self):
        return f"{self.name} ({len(self.items)} skills)"


class Certification(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="certifications")
    name = models.CharField(max_length=160)
    issuer = models.CharField(max_length=160, blank=True)
    date = models.DateField(null=True, blank=True)
    credential_url = models.URLField(blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.name} — {self.issuer}"


class GeneratedPDF(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("compiling", "Compiling"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="generated_pdfs")
    template = models.ForeignKey(
        "templates_lib.ResumeTemplate", on_delete=models.PROTECT
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    file = models.FileField(upload_to="generated_resumes/", null=True, blank=True)
    thumbnail = models.ImageField(upload_to="pdf_thumbnails/", null=True, blank=True)
    compile_log_excerpt = models.TextField(
        blank=True,
        help_text="Last 3000 chars of LaTeX log — server-side only, not shown to users"
    )
    celery_task_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Generated PDF"
        verbose_name_plural = "Generated PDFs"

    def __str__(self):
        return f"PDF #{self.pk} ({self.status}) for Resume #{self.resume_id}"
