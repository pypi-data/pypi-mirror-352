from django.urls import path, include
from . import api

app_name = "configs"


_api_urlpatterns = [
    path(
        "installation-service/",
        api.InstallationServiceListAPI.as_view(),
        name="installation-service-list",
    ),
    path(
        "installation-service/<int:pk>",
        api.InstallationServiceUpdateAPI.as_view(),
        name="installation-service-update",
    ),
    path(
        "installation-service/<int:pk>/",
        api.InstallationServiceDeleteAPI.as_view(),
        name="installation-service-delete",
    ),
    path(
        "installation-service/update-version",
        api.InstallationServiceUpdateAfterDeployAPI.as_view(),
        name="installation-service-update-version-after-deploy",
    ),
]

urlpatterns = [
    path("api/settings/", include((_api_urlpatterns, app_name), namespace="settings"))
]
