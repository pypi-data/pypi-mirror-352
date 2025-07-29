from django.urls import path, re_path
from core import views as core_views
from . import views

urlpatterns = [
    path("api/stripe/create-intent", views.create_intent, name="stripe-create-intent"),
    path("api/stripe/confirm-token", views.confirm_token, name="stripe-confirm-token"),
    path("api/stripe/capture", views.capture, name="stripe-capture"),
    re_path("^stripe/confirm/", core_views.fallback, name="stripe-confirm-page"),
]
