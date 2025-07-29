from django.urls import re_path
from core import views

urlpatterns = [
    re_path(r"^computes/", views.fallback, name="computes"),
]