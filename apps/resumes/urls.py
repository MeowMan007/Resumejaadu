"""apps/resumes/urls.py"""
from django.urls import path
from . import views

app_name = "resumes"

urlpatterns = [
    # Landing & dashboard
    path("", views.landing, name="landing"),
    path("dashboard/", views.dashboard, name="dashboard"),

    # Resume lifecycle
    path("resume/new/", views.create_resume, name="create_resume"),
    path("resume/<int:pk>/delete/", views.delete_resume, name="delete_resume"),
    path("resume/<int:pk>/duplicate/", views.duplicate_resume, name="duplicate_resume"),

    # Wizard steps: /resume/<pk>/step/<step-name>/
    path("resume/<int:pk>/step/<str:step>/", views.wizard_step, name="wizard_step"),

    # PDF generation
    path("resume/<int:pk>/generate-pdf/", views.generate_pdf, name="generate_pdf"),
    path("resume/<int:pk>/pdf-status/<int:gen_pk>/", views.pdf_status, name="pdf_status"),
    path("resume/<int:pk>/download/<int:gen_pk>/", views.download_pdf, name="download_pdf"),
]
