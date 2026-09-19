import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.resumes.models import Resume, PersonalInfo, Experience, ExperienceBullet, Education, Project
from apps.resumes.forms import ExperienceForm
from apps.templates_lib.models import ResumeTemplate
from apps.generator.jinja_env import render_resume_to_tex

User = get_user_model()

@pytest.mark.django_db
class TestResumeWizardAndLatex:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.user = User.objects.create_user(username="wizard_test", email="wizard_test@example.com", password="password123")
        self.template = ResumeTemplate.objects.filter(slug="jakes-resume").first()
        if not self.template:
            self.template = ResumeTemplate.objects.create(
                slug="jakes-resume",
                name="Jake's Resume",
                engine="pdflatex",
                category="single_column"
            )
        self.resume = Resume.objects.create(
            user=self.user,
            title="Software Engineer",
            template=self.template,
        )
        self.personal_info = PersonalInfo.objects.create(
            resume=self.resume,
            full_name="Alice Developer & Architect",
            email="alice@example.com",
            phone="555-0199",
            location="San Francisco, CA",
            linkedin_url="https://linkedin.com/in/alice_dev",
            summary="Experienced in C++ & Python with 100% success rate."
        )

    def test_experience_form_bullets_text_sync(self):
        form_data = {
            "company": "Tech Corp & Co.",
            "role": "Senior Engineer",
            "location": "Remote",
            "bullets_text": "• Spearheaded project X boosting revenue by 40%\n- Designed fault-tolerant API processing 1M requests/sec\nBuilt CI/CD pipeline",
            "order": 0,
        }
        form = ExperienceForm(data=form_data)
        assert form.is_valid(), form.errors
        exp = form.save(commit=False)
        exp.resume = self.resume
        exp.save()
        form._save_bullets(exp)

        bullets = list(exp.bullets.order_by("order").values_list("text", flat=True))
        assert len(bullets) == 3
        assert bullets[0] == "Spearheaded project X boosting revenue by 40%"
        assert bullets[1] == "Designed fault-tolerant API processing 1M requests/sec"
        assert bullets[2] == "Built CI/CD pipeline"

    def test_latex_special_char_escaping_and_contact_line(self):
        exp = Experience.objects.create(
            resume=self.resume,
            company="M&A Tech_Corp",
            role="Lead Developer (C & C++)",
            location="New York",
        )
        ExperienceBullet.objects.create(
            experience=exp,
            text="Increased performance by 50% & saved $100K budget",
            order=0
        )
        Project.objects.create(
            resume=self.resume,
            name="Super_App #1",
            tech_stack="Django & PostgreSQL",
            description="High throughput app"
        )

        tex_output = render_resume_to_tex(self.resume, self.template)
        # Check that characters are escaped properly
        assert r"\&" in tex_output
        assert r"\%" in tex_output
        assert r"\$" in tex_output
        assert r"\_" in tex_output
        # Check contact line has no trailing pipe
        assert "555-0199" in tex_output
        assert r"alice@example.com" in tex_output
        assert r"linkedin.com/in/alice\_dev" in tex_output
        # Verify linewidth was used in Jake's resume
        assert r"\begin{tabular*}{\linewidth}" in tex_output

    def test_resume_deletion_view(self, client):
        client.force_login(self.user)
        url = reverse("resumes:delete_resume", kwargs={"pk": self.resume.pk})
        response = client.post(url)
        assert response.status_code == 302
        assert not Resume.objects.filter(pk=self.resume.pk).exists()
