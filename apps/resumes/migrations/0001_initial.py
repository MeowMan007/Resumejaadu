import django.db.models.deletion
import django.db.models.functions.text
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("templates_lib", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Resume",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(default="Untitled Resume", max_length=120)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("final", "Final")], default="draft", max_length=10)),
                ("target_role", models.CharField(blank=True, help_text="Used to focus AI enhancements", max_length=120)),
                ("current_step", models.PositiveSmallIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="resumes", to=settings.AUTH_USER_MODEL)),
                ("template", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="resumes",
                    to="templates_lib.resumetemplate",
                )),
            ],
            options={"verbose_name": "Resume", "verbose_name_plural": "Resumes", "ordering": ["-updated_at"]},
        ),
        migrations.CreateModel(
            name="PersonalInfo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=120)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(blank=True, max_length=40)),
                ("location", models.CharField(blank=True, max_length=120)),
                ("linkedin_url", models.URLField(blank=True)),
                ("github_url", models.URLField(blank=True)),
                ("portfolio_url", models.URLField(blank=True)),
                ("summary", models.TextField(blank=True, help_text="Professional summary / objective. AI-enhanced field.")),
                ("photo", models.ImageField(blank=True, help_text="Optional headshot. Max 5MB. JPEG/PNG/WebP only.", null=True, upload_to="resume_photos/")),
                ("resume", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="personal_info", to="resumes.resume")),
            ],
        ),
        migrations.CreateModel(
            name="Education",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("institution", models.CharField(max_length=160)),
                ("degree", models.CharField(max_length=160)),
                ("field_of_study", models.CharField(blank=True, max_length=160)),
                ("location", models.CharField(blank=True, max_length=120)),
                ("start_date", models.DateField(blank=True, null=True)),
                ("end_date", models.DateField(blank=True, null=True)),
                ("is_current", models.BooleanField(default=False)),
                ("gpa", models.CharField(blank=True, max_length=20)),
                ("order", models.PositiveIntegerField(default=0)),
                ("resume", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="education", to="resumes.resume")),
            ],
            options={"verbose_name": "Education", "verbose_name_plural": "Education", "ordering": ["order", "-start_date"]},
        ),
        migrations.CreateModel(
            name="Experience",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("company", models.CharField(max_length=160)),
                ("role", models.CharField(max_length=160)),
                ("location", models.CharField(blank=True, max_length=120)),
                ("start_date", models.DateField(blank=True, null=True)),
                ("end_date", models.DateField(blank=True, null=True)),
                ("is_current", models.BooleanField(default=False)),
                ("order", models.PositiveIntegerField(default=0)),
                ("resume", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="experience", to="resumes.resume")),
            ],
            options={"verbose_name": "Experience", "verbose_name_plural": "Experiences", "ordering": ["order", "-start_date"]},
        ),
        migrations.CreateModel(
            name="ExperienceBullet",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text", models.TextField(help_text="Single bullet point. AI-enhanced field.")),
                ("order", models.PositiveIntegerField(default=0)),
                ("experience", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="bullets", to="resumes.experience")),
            ],
            options={"ordering": ["order"]},
        ),
        migrations.CreateModel(
            name="Project",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160)),
                ("tech_stack", models.CharField(blank=True, max_length=200)),
                ("link", models.URLField(blank=True)),
                ("description", models.TextField(blank=True, help_text="AI-enhanced field.")),
                ("order", models.PositiveIntegerField(default=0)),
                ("resume", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="projects", to="resumes.resume")),
            ],
            options={"ordering": ["order"]},
        ),
        migrations.CreateModel(
            name="SkillCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(help_text="e.g. Languages, Frameworks, Tools", max_length=80)),
                ("items", models.JSONField(default=list, help_text="List of skill strings")),
                ("order", models.PositiveIntegerField(default=0)),
                ("resume", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="skill_categories", to="resumes.resume")),
            ],
            options={"verbose_name": "Skill Category", "verbose_name_plural": "Skill Categories", "ordering": ["order"]},
        ),
        migrations.CreateModel(
            name="Certification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160)),
                ("issuer", models.CharField(blank=True, max_length=160)),
                ("date", models.DateField(blank=True, null=True)),
                ("credential_url", models.URLField(blank=True)),
                ("resume", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="certifications", to="resumes.resume")),
            ],
            options={"ordering": ["-date"]},
        ),
        migrations.CreateModel(
            name="GeneratedPDF",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("pending", "Pending"), ("compiling", "Compiling"), ("success", "Success"), ("failed", "Failed")], default="pending", max_length=10)),
                ("file", models.FileField(blank=True, null=True, upload_to="generated_resumes/")),
                ("thumbnail", models.ImageField(blank=True, null=True, upload_to="pdf_thumbnails/")),
                ("compile_log_excerpt", models.TextField(blank=True, help_text="Last 3000 chars of LaTeX log — server-side only, not shown to users")),
                ("celery_task_id", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("resume", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="generated_pdfs", to="resumes.resume")),
                ("template", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="templates_lib.resumetemplate")),
            ],
            options={"verbose_name": "Generated PDF", "verbose_name_plural": "Generated PDFs", "ordering": ["-created_at"]},
        ),
    ]
