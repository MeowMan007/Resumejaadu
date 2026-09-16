"""apps/ai_assistant/urls.py"""
from django.urls import path
from . import views

app_name = "ai_assistant"

urlpatterns = [
    path("enhance-summary/", views.enhance_summary, name="enhance_summary"),
    path("enhance-bullet/", views.enhance_bullet, name="enhance_bullet"),
    path("enhance-project/", views.enhance_project, name="enhance_project"),
    path("categorize-skills/", views.categorize_skills, name="categorize_skills"),
    path("tailor/", views.tailor_to_job, name="tailor_to_job"),
]
