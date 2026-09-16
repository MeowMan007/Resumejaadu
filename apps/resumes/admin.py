"""
apps/resumes/admin.py — Admin registration for all Resume models.
"""
from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Resume, PersonalInfo, Education, Experience,
    ExperienceBullet, Project, SkillCategory, Certification, GeneratedPDF
)


class PersonalInfoInline(admin.StackedInline):
    model = PersonalInfo
    can_delete = False
    extra = 0


class ExperienceBulletInline(admin.TabularInline):
    model = ExperienceBullet
    extra = 1
    ordering = ["order"]


class EducationInline(admin.TabularInline):
    model = Education
    extra = 0
    ordering = ["order"]


class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 0
    ordering = ["order"]
    show_change_link = True


class ProjectInline(admin.TabularInline):
    model = Project
    extra = 0
    ordering = ["order"]


class SkillCategoryInline(admin.TabularInline):
    model = SkillCategory
    extra = 0
    ordering = ["order"]


class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 0


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "template", "status", "current_step", "updated_at"]
    list_filter = ["status", "template"]
    search_fields = ["title", "user__email", "target_role"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [
        PersonalInfoInline, EducationInline, ExperienceInline,
        ProjectInline, SkillCategoryInline, CertificationInline
    ]


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ["role", "company", "resume", "start_date", "end_date", "is_current"]
    inlines = [ExperienceBulletInline]


@admin.register(GeneratedPDF)
class GeneratedPDFAdmin(admin.ModelAdmin):
    list_display = ["pk", "resume", "template", "status", "created_at", "pdf_link"]
    list_filter = ["status"]
    readonly_fields = ["created_at", "celery_task_id"]

    def pdf_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">Download</a>', obj.file.url)
        return "—"
    pdf_link.short_description = "PDF"
