"""
apps/resumes/views.py — Wizard views, dashboard, PDF generation, and download.
"""
import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

from apps.templates_lib.models import ResumeTemplate

from .forms import (
    ResumeCreateForm, PersonalInfoForm, EducationFormSet,
    ExperienceFormSet, ExperienceBulletFormSet, ProjectFormSet,
    SkillCategoryFormSet, CertificationFormSet,
)
from .models import Resume, PersonalInfo, Experience, GeneratedPDF

logger = logging.getLogger(__name__)

# ─── Wizard Step Map ──────────────────────────────────────────────────────────
WIZARD_STEPS = [
    "personal-info",
    "summary",
    "experience",
    "education",
    "skills",
    "projects",
    "certifications",
    "template",
    "review",
]

STEP_TITLES = {
    "personal-info": ("Personal Info", "Tell us about yourself"),
    "summary": ("Summary", "Your career in 2–3 sentences"),
    "experience": ("Experience", "Your work history"),
    "education": ("Education", "Degrees & courses"),
    "skills": ("Skills", "Your technical & soft skills"),
    "projects": ("Projects", "Side projects & open source"),
    "certifications": ("Certifications", "Courses & credentials"),
    "template": ("Choose Template", "Pick your resume style"),
    "review": ("Review & Download", "Preview and export your resume"),
}


def _get_step_index(step: str) -> int:
    try:
        return WIZARD_STEPS.index(step)
    except ValueError:
        return 0


def _assert_owns_resume(resume, user):
    if resume.user_id != user.pk:
        raise Http404


# ─── Landing & Dashboard ──────────────────────────────────────────────────────

def landing(request):
    """Public landing page."""
    if request.user.is_authenticated:
        return redirect("resumes:dashboard")
    return render(request, "landing.html")


@login_required
def dashboard(request):
    """'My Resumes' dashboard."""
    resumes = (
        Resume.objects.filter(user=request.user)
        .select_related("template", "personal_info")
        .prefetch_related("generated_pdfs")
        .order_by("-updated_at")
    )
    return render(request, "dashboard/dashboard.html", {"resumes": resumes})


# ─── Create Resume ────────────────────────────────────────────────────────────

@login_required
def create_resume(request):
    """Create a new Resume and redirect to step 1."""
    if request.method == "POST":
        form = ResumeCreateForm(request.POST)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()
            # Create blank PersonalInfo
            PersonalInfo.objects.get_or_create(
                resume=resume,
                defaults={"full_name": "", "email": request.user.email}
            )
            return redirect("resumes:wizard_step", pk=resume.pk, step="personal-info")
    else:
        form = ResumeCreateForm(initial={"title": "My Resume"})
    return render(request, "resumes/create.html", {"form": form})


# ─── Wizard Step Router ───────────────────────────────────────────────────────

@login_required
def wizard_step(request, pk: int, step: str):
    """Route to the correct wizard step handler."""
    resume = get_object_or_404(Resume, pk=pk)
    _assert_owns_resume(resume, request.user)

    if step not in WIZARD_STEPS:
        return redirect("resumes:wizard_step", pk=pk, step=WIZARD_STEPS[0])

    handler_map = {
        "personal-info": _step_personal_info,
        "summary": _step_summary,
        "experience": _step_experience,
        "education": _step_education,
        "skills": _step_skills,
        "projects": _step_projects,
        "certifications": _step_certifications,
        "template": _step_template,
        "review": _step_review,
    }
    return handler_map[step](request, resume, step)


def _wizard_context(resume, step: str) -> dict:
    """Base context for all wizard steps."""
    step_idx = _get_step_index(step)
    return {
        "resume": resume,
        "step": step,
        "step_idx": step_idx,
        "step_count": len(WIZARD_STEPS),
        "steps": WIZARD_STEPS,
        "step_titles": STEP_TITLES,
        "title": STEP_TITLES.get(step, ("", ""))[0],
        "subtitle": STEP_TITLES.get(step, ("", ""))[1],
        "prev_step": WIZARD_STEPS[step_idx - 1] if step_idx > 0 else None,
        "next_step": WIZARD_STEPS[step_idx + 1] if step_idx < len(WIZARD_STEPS) - 1 else None,
        "progress_pct": int((step_idx + 1) / len(WIZARD_STEPS) * 100),
    }


def _step_personal_info(request, resume, step):
    personal_info, _ = PersonalInfo.objects.get_or_create(
        resume=resume, defaults={"full_name": "", "email": resume.user.email}
    )
    if request.method == "POST":
        form = PersonalInfoForm(request.POST, request.FILES, instance=personal_info)
        if form.is_valid():
            form.save()
            resume.current_step = max(resume.current_step, 1)
            resume.save(update_fields=["current_step"])
            if "save_and_continue" in request.POST:
                return redirect("resumes:wizard_step", pk=resume.pk, step="summary")
            messages.success(request, "Personal info saved.")
    else:
        form = PersonalInfoForm(instance=personal_info)
    ctx = _wizard_context(resume, step)
    ctx["form"] = form
    return render(request, "resumes/steps/personal_info.html", ctx)


def _step_summary(request, resume, step):
    personal_info, _ = PersonalInfo.objects.get_or_create(
        resume=resume, defaults={"full_name": "", "email": resume.user.email}
    )
    if request.method == "POST":
        summary = request.POST.get("summary", "")
        personal_info.summary = summary
        personal_info.save(update_fields=["summary"])
        resume.current_step = max(resume.current_step, 2)
        resume.save(update_fields=["current_step"])
        if "save_and_continue" in request.POST:
            return redirect("resumes:wizard_step", pk=resume.pk, step="experience")
        messages.success(request, "Summary saved.")
    ctx = _wizard_context(resume, step)
    ctx["personal_info"] = personal_info
    return render(request, "resumes/steps/summary.html", ctx)


def _step_experience(request, resume, step):
    ExperienceFS = ExperienceFormSet
    if request.method == "POST":
        formset = ExperienceFS(request.POST, instance=resume)
        if formset.is_valid():
            instances = formset.save()
            # Process bullet sub-formsets for each saved experience
            for i, exp_form in enumerate(formset.forms):
                if exp_form.instance.pk and not exp_form.cleaned_data.get("DELETE"):
                    bullet_fs = ExperienceBulletFormSet(
                        request.POST,
                        instance=exp_form.instance,
                        prefix=f"bullets_{exp_form.instance.pk}",
                    )
                    if bullet_fs.is_valid():
                        bullet_fs.save()
            resume.current_step = max(resume.current_step, 3)
            resume.save(update_fields=["current_step"])
            if "save_and_continue" in request.POST:
                return redirect("resumes:wizard_step", pk=resume.pk, step="education")
    else:
        formset = ExperienceFS(instance=resume)

    # Attach bullet formsets to each experience form
    experience_with_bullets = []
    for form in formset.forms:
        if form.instance.pk:
            bullet_fs = ExperienceBulletFormSet(
                instance=form.instance,
                prefix=f"bullets_{form.instance.pk}",
            )
        else:
            bullet_fs = None
        experience_with_bullets.append((form, bullet_fs))

    ctx = _wizard_context(resume, step)
    ctx["formset"] = formset
    ctx["experience_with_bullets"] = experience_with_bullets
    return render(request, "resumes/steps/experience.html", ctx)


def _step_education(request, resume, step):
    EducationFS = EducationFormSet
    if request.method == "POST":
        formset = EducationFS(request.POST, instance=resume)
        if formset.is_valid():
            formset.save()
            resume.current_step = max(resume.current_step, 4)
            resume.save(update_fields=["current_step"])
            if "save_and_continue" in request.POST:
                return redirect("resumes:wizard_step", pk=resume.pk, step="skills")
    else:
        formset = EducationFS(instance=resume)
    ctx = _wizard_context(resume, step)
    ctx["formset"] = formset
    return render(request, "resumes/steps/education.html", ctx)


def _step_skills(request, resume, step):
    SkillFS = SkillCategoryFormSet
    if request.method == "POST":
        formset = SkillFS(request.POST, instance=resume)
        if formset.is_valid():
            formset.save()
            resume.current_step = max(resume.current_step, 5)
            resume.save(update_fields=["current_step"])
            if "save_and_continue" in request.POST:
                return redirect("resumes:wizard_step", pk=resume.pk, step="projects")
    else:
        formset = SkillFS(instance=resume)
    ctx = _wizard_context(resume, step)
    ctx["formset"] = formset
    return render(request, "resumes/steps/skills.html", ctx)


def _step_projects(request, resume, step):
    # Check if the selected template supports projects
    if resume.template and not resume.template.supports_projects:
        return redirect("resumes:wizard_step", pk=resume.pk, step="certifications")

    ProjectFS = ProjectFormSet
    if request.method == "POST":
        formset = ProjectFS(request.POST, instance=resume)
        if formset.is_valid():
            formset.save()
            resume.current_step = max(resume.current_step, 6)
            resume.save(update_fields=["current_step"])
            if "save_and_continue" in request.POST:
                return redirect("resumes:wizard_step", pk=resume.pk, step="certifications")
    else:
        formset = ProjectFS(instance=resume)
    ctx = _wizard_context(resume, step)
    ctx["formset"] = formset
    return render(request, "resumes/steps/projects.html", ctx)


def _step_certifications(request, resume, step):
    CertFS = CertificationFormSet
    if request.method == "POST":
        formset = CertFS(request.POST, instance=resume)
        if formset.is_valid():
            formset.save()
            resume.current_step = max(resume.current_step, 7)
            resume.save(update_fields=["current_step"])
            if "save_and_continue" in request.POST:
                return redirect("resumes:wizard_step", pk=resume.pk, step="template")
    else:
        formset = CertFS(instance=resume)
    ctx = _wizard_context(resume, step)
    ctx["formset"] = formset
    return render(request, "resumes/steps/certifications.html", ctx)


def _step_template(request, resume, step):
    templates = ResumeTemplate.objects.filter(is_active=True).order_by("category", "name")
    if request.method == "POST":
        template_slug = request.POST.get("template_slug")
        if template_slug:
            try:
                tmpl = ResumeTemplate.objects.get(slug=template_slug, is_active=True)
                resume.template = tmpl
                resume.current_step = max(resume.current_step, 8)
                resume.save(update_fields=["template", "current_step"])
                messages.success(request, f"Template '{tmpl.name}' selected!")
                if "save_and_continue" in request.POST:
                    return redirect("resumes:wizard_step", pk=resume.pk, step="review")
            except ResumeTemplate.DoesNotExist:
                messages.error(request, "Invalid template selected.")

    # Group templates by category
    categories = {}
    for tmpl in templates:
        cat = tmpl.get_category_display()
        categories.setdefault(cat, []).append(tmpl)

    ctx = _wizard_context(resume, step)
    ctx["templates"] = templates
    ctx["categories"] = categories
    return render(request, "resumes/steps/template_gallery.html", ctx)


def _step_review(request, resume, step):
    latest_pdf = resume.generated_pdfs.order_by("-created_at").first()
    ctx = _wizard_context(resume, step)
    ctx["latest_pdf"] = latest_pdf
    ctx.update({
        "personal": getattr(resume, "personal_info", None),
        "experience": resume.experience.prefetch_related("bullets").order_by("order"),
        "education": resume.education.order_by("order"),
        "skills": resume.skill_categories.order_by("order"),
        "projects": resume.projects.order_by("order"),
        "certifications": resume.certifications.order_by("-date"),
    })
    return render(request, "resumes/steps/review.html", ctx)


# ─── PDF Generation ───────────────────────────────────────────────────────────

@login_required
@require_POST
def generate_pdf(request, pk: int):
    """Enqueue PDF generation and return task ID."""
    resume = get_object_or_404(Resume, pk=pk)
    _assert_owns_resume(resume, request.user)

    if not resume.template:
        return JsonResponse({"error": "Please select a template first."}, status=400)

    # Create a GeneratedPDF record
    gen = GeneratedPDF.objects.create(
        resume=resume,
        template=resume.template,
        status="pending",
    )

    # Enqueue the Celery task
    from apps.generator.tasks import generate_resume_pdf
    task = generate_resume_pdf.delay(gen.pk)
    gen.celery_task_id = task.id
    gen.save(update_fields=["celery_task_id"])

    return JsonResponse({
        "task_id": task.id,
        "generated_pdf_id": gen.pk,
        "status": "pending",
        "poll_url": f"/resumes/{pk}/pdf-status/{gen.pk}/",
    })


@login_required
def pdf_status(request, pk: int, gen_pk: int):
    """Poll endpoint for PDF generation status."""
    resume = get_object_or_404(Resume, pk=pk)
    _assert_owns_resume(resume, request.user)
    gen = get_object_or_404(GeneratedPDF, pk=gen_pk, resume=resume)

    data = {
        "status": gen.status,
        "generated_pdf_id": gen.pk,
    }
    if gen.status == "success":
        data["pdf_url"] = gen.file.url if gen.file else None
        data["thumbnail_url"] = gen.thumbnail.url if gen.thumbnail else None
    elif gen.status == "failed":
        data["error"] = "PDF compilation failed. Please check your data and try again."

    if request.headers.get("HX-Request"):
        return render(request, "resumes/partials/pdf_status.html", {
            "gen": gen,
            "resume": resume,
            **data
        })
    return JsonResponse(data)


@login_required
def download_pdf(request, pk: int, gen_pk: int):
    """Serve the generated PDF as a download."""
    resume = get_object_or_404(Resume, pk=pk)
    _assert_owns_resume(resume, request.user)
    gen = get_object_or_404(GeneratedPDF, pk=gen_pk, resume=resume, status="success")

    if not gen.file:
        raise Http404("PDF file not found.")

    import os
    filename = f"{resume.title.replace(' ', '_')}.pdf"
    response = HttpResponse(gen.file.read(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


# ─── Resume Management ────────────────────────────────────────────────────────

@login_required
@require_POST
def delete_resume(request, pk: int):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    resume.delete()
    messages.success(request, "Resume deleted.")
    return redirect("resumes:dashboard")


@login_required
@require_POST
def duplicate_resume(request, pk: int):
    """Duplicate a resume (all data) onto the same or a different template."""
    import copy
    original = get_object_or_404(Resume, pk=pk, user=request.user)

    # Create new Resume
    new_resume = Resume.objects.create(
        user=request.user,
        title=f"{original.title} (Copy)",
        template=original.template,
        target_role=original.target_role,
    )

    # Copy PersonalInfo
    if hasattr(original, "personal_info"):
        pi = original.personal_info
        pi.pk = None
        pi.resume = new_resume
        pi.save()

    # Copy Education
    for edu in original.education.all():
        edu.pk = None
        edu.resume = new_resume
        edu.save()

    # Copy Experience + Bullets
    for exp in original.experience.prefetch_related("bullets").all():
        bullets = list(exp.bullets.all())
        exp.pk = None
        exp.resume = new_resume
        exp.save()
        for bullet in bullets:
            bullet.pk = None
            bullet.experience = exp
            bullet.save()

    # Copy Projects
    for proj in original.projects.all():
        proj.pk = None
        proj.resume = new_resume
        proj.save()

    # Copy SkillCategories
    for sc in original.skill_categories.all():
        sc.pk = None
        sc.resume = new_resume
        sc.save()

    # Copy Certifications
    for cert in original.certifications.all():
        cert.pk = None
        cert.resume = new_resume
        cert.save()

    messages.success(request, f"Resume duplicated as '{new_resume.title}'.")
    return redirect("resumes:wizard_step", pk=new_resume.pk, step="personal-info")
