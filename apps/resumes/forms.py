"""
apps/resumes/forms.py — All wizard step forms for resume building.
"""
from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet

from .models import (
    Resume, PersonalInfo, Education, Experience,
    ExperienceBullet, Project, SkillCategory, Certification
)


class ResumeCreateForm(forms.ModelForm):
    """Step 0: Create a new resume (title + target role)."""
    class Meta:
        model = Resume
        fields = ["title", "target_role"]
        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "e.g. Software Engineer Resume 2024",
                "class": "form-input",
                "id": "id_title",
            }),
            "target_role": forms.TextInput(attrs={
                "placeholder": "e.g. Senior Backend Engineer",
                "class": "form-input",
                "id": "id_target_role",
            }),
        }


class PersonalInfoForm(forms.ModelForm):
    """Step 1: Personal information."""
    class Meta:
        model = PersonalInfo
        fields = [
            "full_name", "email", "phone", "location",
            "linkedin_url", "github_url", "portfolio_url",
            "summary", "photo"
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-input", "id": "id_full_name", "placeholder": "Jane Doe"}),
            "email": forms.EmailInput(attrs={"class": "form-input", "id": "id_email", "placeholder": "jane@example.com"}),
            "phone": forms.TextInput(attrs={"class": "form-input", "id": "id_phone", "placeholder": "+1 (555) 000-0000"}),
            "location": forms.TextInput(attrs={"class": "form-input", "id": "id_location", "placeholder": "San Francisco, CA"}),
            "linkedin_url": forms.URLInput(attrs={"class": "form-input", "id": "id_linkedin_url", "placeholder": "https://linkedin.com/in/janedoe"}),
            "github_url": forms.URLInput(attrs={"class": "form-input", "id": "id_github_url", "placeholder": "https://github.com/janedoe"}),
            "portfolio_url": forms.URLInput(attrs={"class": "form-input", "id": "id_portfolio_url", "placeholder": "https://janedoe.dev"}),
            "summary": forms.Textarea(attrs={
                "class": "form-textarea", "id": "id_summary", "rows": 4,
                "placeholder": "2–3 sentences about your career highlights and goals…",
            }),
            "photo": forms.FileInput(attrs={"class": "form-file", "id": "id_photo", "accept": "image/jpeg,image/png,image/webp"}),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo:
            from django.conf import settings
            # Validate extension
            ext = photo.name.rsplit(".", 1)[-1].lower()
            allowed = getattr(settings, "ALLOWED_IMAGE_EXTENSIONS", ["jpg", "jpeg", "png", "webp"])
            if ext not in allowed:
                raise forms.ValidationError(f"Unsupported format. Use: {', '.join(allowed)}")
            # Validate size
            max_mb = getattr(settings, "MAX_PHOTO_SIZE_MB", 5)
            if photo.size > max_mb * 1024 * 1024:
                raise forms.ValidationError(f"Photo must be under {max_mb}MB.")
            # Re-encode with Pillow to strip EXIF/metadata and validate
            try:
                from PIL import Image
                import io
                img = Image.open(photo)
                img.verify()
                photo.seek(0)
                img = Image.open(photo)
                img = img.convert("RGB")
                output = io.BytesIO()
                img.save(output, format="JPEG", quality=85, optimize=True)
                output.seek(0)
                from django.core.files.uploadedfile import InMemoryUploadedFile
                return InMemoryUploadedFile(
                    output, "ImageField",
                    f"{photo.name.rsplit('.', 1)[0]}.jpg",
                    "image/jpeg", output.getbuffer().nbytes, None
                )
            except Exception:
                raise forms.ValidationError("Invalid image file.")
        return photo


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ["institution", "degree", "field_of_study", "location", "start_date", "end_date", "is_current", "gpa", "order"]
        widgets = {
            "institution": forms.TextInput(attrs={"class": "form-input", "placeholder": "MIT"}),
            "degree": forms.TextInput(attrs={"class": "form-input", "placeholder": "B.S. Computer Science"}),
            "field_of_study": forms.TextInput(attrs={"class": "form-input", "placeholder": "Computer Science"}),
            "location": forms.TextInput(attrs={"class": "form-input", "placeholder": "Cambridge, MA"}),
            "start_date": forms.DateInput(attrs={"class": "form-input", "type": "month"}),
            "end_date": forms.DateInput(attrs={"class": "form-input", "type": "month"}),
            "gpa": forms.TextInput(attrs={"class": "form-input", "placeholder": "3.8/4.0"}),
            "order": forms.HiddenInput(),
        }


class ExperienceForm(forms.ModelForm):
    bullets_text = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": "form-textarea",
            "rows": 4,
            "placeholder": "• Led migration of monolithic API to microservices, reducing response time by 40%\n• Designed high-throughput data pipeline processing 2TB daily",
        }),
        required=False,
        label="Achievement Bullets",
        help_text="Enter bullets (one per line, starting with •, -, or plain text)",
    )

    class Meta:
        model = Experience
        fields = ["company", "role", "location", "start_date", "end_date", "is_current", "order"]
        widgets = {
            "company": forms.TextInput(attrs={"class": "form-input", "placeholder": "Google"}),
            "role": forms.TextInput(attrs={"class": "form-input", "placeholder": "Software Engineer"}),
            "location": forms.TextInput(attrs={"class": "form-input", "placeholder": "Mountain View, CA"}),
            "start_date": forms.DateInput(attrs={"class": "form-input", "type": "month"}),
            "end_date": forms.DateInput(attrs={"class": "form-input", "type": "month"}),
            "order": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            bullets = list(self.instance.bullets.order_by("order").values_list("text", flat=True))
            if bullets:
                self.fields["bullets_text"].initial = "\n".join(bullets)

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit:
            self._save_bullets(instance)
        return instance

    def _save_bullets(self, instance):
        bullets_raw = self.cleaned_data.get("bullets_text", "")
        lines = [line.strip() for line in bullets_raw.splitlines() if line.strip()]
        clean_lines = []
        for l in lines:
            cleaned = l.lstrip("•-* \t")
            if cleaned:
                clean_lines.append(cleaned)

        existing = list(instance.bullets.order_by("order"))
        for i, text in enumerate(clean_lines):
            if i < len(existing):
                bullet = existing[i]
                if bullet.text != text or bullet.order != i:
                    bullet.text = text
                    bullet.order = i
                    bullet.save(update_fields=["text", "order"])
            else:
                ExperienceBullet.objects.create(
                    experience=instance,
                    text=text,
                    order=i
                )
        if len(existing) > len(clean_lines):
            for bullet in existing[len(clean_lines):]:
                bullet.delete()


class ExperienceBulletForm(forms.ModelForm):
    class Meta:
        model = ExperienceBullet
        fields = ["text", "order"]
        widgets = {
            "text": forms.Textarea(attrs={
                "class": "form-textarea",
                "rows": 2,
                "placeholder": "Led migration of monolithic API to microservices, reducing response time by 40%…",
            }),
            "order": forms.HiddenInput(),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "tech_stack", "link", "description", "order"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "ResumeJaadu"}),
            "tech_stack": forms.TextInput(attrs={"class": "form-input", "placeholder": "Django, PostgreSQL, Celery, Redis"}),
            "link": forms.URLInput(attrs={"class": "form-input", "placeholder": "https://github.com/..."}),
            "description": forms.Textarea(attrs={"class": "form-textarea", "rows": 3, "placeholder": "What does this project do? What impact did it have?"}),
            "order": forms.HiddenInput(),
        }


class SkillCategoryForm(forms.ModelForm):
    items_text = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Python, Django, PostgreSQL, Redis…",
        }),
        help_text="Comma-separated list of skills",
        required=False,
        label="Skills",
    )

    class Meta:
        model = SkillCategory
        fields = ["name", "order"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Languages"}),
            "order": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-populate items_text from existing items JSONField
        if self.instance and self.instance.pk and self.instance.items:
            self.fields["items_text"].initial = ", ".join(self.instance.items)

    def save(self, commit=True):
        instance = super().save(commit=False)
        items_text = self.cleaned_data.get("items_text", "")
        instance.items = [s.strip() for s in items_text.split(",") if s.strip()]
        if commit:
            instance.save()
        return instance


class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ["name", "issuer", "date", "credential_url"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "AWS Solutions Architect"}),
            "issuer": forms.TextInput(attrs={"class": "form-input", "placeholder": "Amazon Web Services"}),
            "date": forms.DateInput(attrs={"class": "form-input", "type": "month"}),
            "credential_url": forms.URLInput(attrs={"class": "form-input", "placeholder": "https://..."}),
        }


# ─── Formsets ─────────────────────────────────────────────────────────────────

EducationFormSet = inlineformset_factory(
    Resume, Education,
    form=EducationForm,
    extra=1, can_delete=True, min_num=0, max_num=10,
)

ExperienceFormSet = inlineformset_factory(
    Resume, Experience,
    form=ExperienceForm,
    extra=1, can_delete=True, min_num=0, max_num=15,
)

ExperienceBulletFormSet = inlineformset_factory(
    Experience, ExperienceBullet,
    form=ExperienceBulletForm,
    extra=2, can_delete=True, min_num=0, max_num=8,
)

ProjectFormSet = inlineformset_factory(
    Resume, Project,
    form=ProjectForm,
    extra=1, can_delete=True, min_num=0, max_num=10,
)

SkillCategoryFormSet = inlineformset_factory(
    Resume, SkillCategory,
    form=SkillCategoryForm,
    extra=1, can_delete=True, min_num=0, max_num=8,
)

CertificationFormSet = inlineformset_factory(
    Resume, Certification,
    form=CertificationForm,
    extra=1, can_delete=True, min_num=0, max_num=10,
)
