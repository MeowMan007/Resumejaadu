"""apps/templates_lib/views.py — Template gallery standalone view."""
from django.shortcuts import render
from .models import ResumeTemplate


def gallery(request):
    templates = ResumeTemplate.objects.filter(is_active=True).order_by("category", "name")
    categories = {}
    for tmpl in templates:
        cat = tmpl.get_category_display()
        categories.setdefault(cat, []).append(tmpl)
    return render(request, "templates_lib/gallery.html", {
        "templates": templates,
        "categories": categories,
    })
