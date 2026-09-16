from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ResumeTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(help_text="Matches the folder name in resume_templates/", unique=True)),
                ("name", models.CharField(max_length=120)),
                ("source_url", models.URLField(help_text="Original Overleaf or GitHub URL")),
                ("license", models.CharField(help_text="e.g. LPPL 1.3c, MIT, CC BY 4.0", max_length=80)),
                ("engine", models.CharField(
                    choices=[("pdflatex", "pdfLaTeX"), ("xelatex", "XeLaTeX"), ("lualatex", "LuaLaTeX")],
                    max_length=10,
                )),
                ("category", models.CharField(
                    choices=[
                        ("single_column", "Single Column"),
                        ("two_column", "Two Column / Sidebar"),
                        ("academic", "Academic / CV"),
                        ("creative", "Creative / Colorful"),
                    ],
                    max_length=20,
                )),
                ("supports_photo", models.BooleanField(default=False)),
                ("supports_projects", models.BooleanField(default=True)),
                ("supports_certifications", models.BooleanField(default=True)),
                ("is_one_page_design", models.BooleanField(default=True)),
                ("ats_friendly", models.BooleanField(
                    default=False,
                    help_text="True if template is designed for ATS parsing (minimal graphics/tables)",
                )),
                ("thumbnail", models.ImageField(
                    blank=True, null=True,
                    help_text="Auto-generated from compiled sample or manually uploaded",
                    upload_to="template_thumbnails/",
                )),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Resume Template",
                "verbose_name_plural": "Resume Templates",
                "ordering": ["name"],
            },
        ),
    ]
