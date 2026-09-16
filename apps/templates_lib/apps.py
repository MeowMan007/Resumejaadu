"""apps/templates_lib/apps.py"""
from django.apps import AppConfig


class TemplatesLibConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.templates_lib"
    label = "templates_lib"
