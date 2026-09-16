"""
tests/test_models.py

Unit tests for core resume models: creation, relationships, str methods,
computed properties, and model-level logic.
"""
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.resumes.models import (
    Resume, PersonalInfo, Education, Experience,
    ExperienceBullet, Project, SkillCategory, Certification, GeneratedPDF
)
from apps.templates_lib.models import ResumeTemplate

User = get_user_model()


def make_user(email="test@example.com"):
    return User.objects.create_user(
        username=email, email=email, password="testpass123"
    )


def make_template():
    return ResumeTemplate.objects.create(
        slug="test-tmpl",
        name="Test Template",
        source_url="https://example.com",
        license="MIT",
        engine="pdflatex",
        category="single_column",
    )


class ResumeModelTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.tmpl = make_template()

    def test_create_resume(self):
        resume = Resume.objects.create(user=self.user, title="My Resume")
        self.assertEqual(resume.status, "draft")
        self.assertEqual(resume.current_step, 0)
        self.assertIsNone(resume.template)

    def test_resume_str(self):
        resume = Resume.objects.create(user=self.user, title="Test")
        self.assertIn("Test", str(resume))
        self.assertIn(self.user.email, str(resume))

    def test_resume_latest_pdf_none(self):
        resume = Resume.objects.create(user=self.user)
        self.assertIsNone(resume.latest_pdf)

    def test_resume_latest_pdf(self):
        resume = Resume.objects.create(user=self.user, template=self.tmpl)
        pdf = GeneratedPDF.objects.create(resume=resume, template=self.tmpl, status="success")
        self.assertEqual(resume.latest_pdf.pk, pdf.pk)

    def test_get_absolute_url(self):
        resume = Resume.objects.create(user=self.user)
        url = resume.get_absolute_url()
        self.assertIn(str(resume.pk), url)
        self.assertIn("personal-info", url)


class PersonalInfoModelTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.resume = Resume.objects.create(user=self.user)

    def test_create_personal_info(self):
        pi = PersonalInfo.objects.create(
            resume=self.resume,
            full_name="Jane Doe",
            email="jane@example.com",
        )
        self.assertEqual(pi.resume, self.resume)
        self.assertEqual(self.resume.personal_info, pi)

    def test_personal_info_str(self):
        pi = PersonalInfo.objects.create(
            resume=self.resume, full_name="X", email="x@x.com"
        )
        self.assertIn(str(self.resume.pk), str(pi))


class ExperienceModelTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.resume = Resume.objects.create(user=self.user)

    def test_create_experience_with_bullets(self):
        exp = Experience.objects.create(
            resume=self.resume, company="Acme", role="Engineer"
        )
        b1 = ExperienceBullet.objects.create(experience=exp, text="Built X", order=0)
        b2 = ExperienceBullet.objects.create(experience=exp, text="Improved Y", order=1)
        self.assertEqual(exp.bullets.count(), 2)
        self.assertEqual(list(exp.bullets.values_list("order", flat=True)), [0, 1])

    def test_experience_str(self):
        exp = Experience.objects.create(resume=self.resume, company="Corp", role="Dev")
        self.assertIn("Dev", str(exp))
        self.assertIn("Corp", str(exp))


class SkillCategoryModelTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.resume = Resume.objects.create(user=self.user)

    def test_skill_category_json_field(self):
        sc = SkillCategory.objects.create(
            resume=self.resume,
            name="Languages",
            items=["Python", "Go", "TypeScript"],
        )
        self.assertEqual(len(sc.items), 3)
        self.assertIn("Python", sc.items)
        self.assertIn(str(3), str(sc))

    def test_empty_items_default(self):
        sc = SkillCategory.objects.create(resume=self.resume, name="Empty")
        self.assertEqual(sc.items, [])


class ResumeTemplateModelTest(TestCase):

    def test_create_template(self):
        tmpl = make_template()
        self.assertEqual(tmpl.slug, "test-tmpl")
        self.assertTrue(tmpl.is_active)

    def test_template_str(self):
        tmpl = make_template()
        self.assertIn("Test Template", str(tmpl))
        self.assertIn("pdfLaTeX", str(tmpl))

    def test_template_dir_property(self):
        tmpl = make_template()
        from django.conf import settings
        expected = settings.RESUME_TEMPLATE_ROOT / "test-tmpl"
        self.assertEqual(tmpl.template_dir, expected)

    def test_jinja_template_path(self):
        tmpl = make_template()
        self.assertTrue(str(tmpl.jinja_template_path).endswith("template.tex.jinja"))
