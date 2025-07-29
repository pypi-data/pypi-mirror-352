from django.urls import path, include
from . import views

app_name = 'workflows'

urlpatterns = [
    path('api/workflows-token', views.workflows_token, name='get-workflows-token'),
]
