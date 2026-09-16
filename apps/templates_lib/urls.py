"""apps/templates_lib/urls.py"""
from django.urls import path
from . import views

app_name = "templates_lib"

urlpatterns = [
    path("", views.gallery, name="gallery"),
]
