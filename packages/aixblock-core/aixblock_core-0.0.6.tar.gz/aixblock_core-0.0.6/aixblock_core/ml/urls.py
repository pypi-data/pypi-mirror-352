"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
from django.urls import path, include

from . import api

app_name = 'ml'

# ML backend CRUD
_api_urlpatterns = [
    # All ml backends
    path("docker", api.MLBackendDockerAPI.as_view(), name="ml-docker"),
    path("", api.MLBackendListAPI.as_view(), name="ml-list"),
    path("ml-deploy-list", api.MLBackendDeployAPI.as_view(), name="ml-deploy-list"),
    path("history-deploy-list", api.HistoryDeployAPI.as_view(), name="ml-deploy-list"),
    path("monitor", api.MLBackendListMonitorAPI.as_view(), name="ml-list-monitor"),
    path("admin/", api.MLBackendListAdminViewAPI.as_view(), name="ml-admin-list"),
    path("<int:pk>", api.MLBackendDetailAPI.as_view(), name="ml-detail"),
    path("<int:pk>/train", api.MLBackendTrainAPI.as_view(), name="ml-train"),
    path(
        "<int:pk>/stop-train", api.MLBackendStopTrainAPI.as_view(), name="ml-stop-train"
    ),
    path(
        "<int:pk>/interactive-annotating",
        api.MLBackendInteractiveAnnotating.as_view(),
        name="ml-interactive-annotating",
    ),
    path("<int:pk>/versions", api.MLBackendVersionsAPI.as_view(), name="ml-versions"),
    path("ml_url", api.MLBackendUrlViewAPI.as_view(), name="ml-url"),
    path("update-ram-ml/", api.MLBackendUpdateRam.as_view(), name="update-ml-ram"),
    # path('queue', api.MLBackendQueueAPI.as_view(), name='ml-queue'),
    path("<int:pk>/reset", api.MLBackendResetAPI.as_view(), name="ml_backend_reset"),
    path(
        "<int:pk>/update-config",
        api.MLBackendConfigAPI.as_view(),
        name="ml_backend_update_config",
    ),
    path(
        "ml-network/",
        api.MLBackendListNetworkAPI.as_view(),
        name="ml-backend-list-network",
    ),
    path(
        "ml-network/join/<int:network_id>/",
        api.JoinMLBackendToNetwork.as_view(),
        name="join_ml_backend_to_network",
    ),
    path(
        "ml-network/disconnect/<int:network_id>/",
        api.DisconnectNetwork.as_view(),
        name="disconnect_network",
    ),
    path(
        "ml-network/add-compute/<int:network_id>/",
        api.AddComputeToNetwork.as_view(),
        name="add-compute-to-network",
    ),
]

_api_trainjob_urlpatterns = [
    path('admin/', api.MLBackendTrainJobListAdminViewAPI.as_view(), name='ml-admin-list'),
]

urlpatterns = [
    path('api/ml/', include((_api_urlpatterns, app_name), namespace='api')),
    path('api/mltrainjob/', include((_api_trainjob_urlpatterns, app_name), namespace='api-admin')),
]
