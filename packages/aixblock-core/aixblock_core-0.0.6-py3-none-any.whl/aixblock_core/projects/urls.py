"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import data_export.api
from django.shortcuts import redirect
from django.urls import include, path, re_path

from . import api, views, crawl_api
from core import views as core_views

app_name = 'projects'

# reverse for projects:name
_urlpatterns = [
    path('', views.project_list, name='project-index'),
    path('<int:pk>/settings/', views.project_settings, name='project-settings', kwargs={'sub_path': ''}),
    path('<int:pk>/editor/', views.project_editor, name='project-editor', kwargs={'sub_path': ''}),
    path('<int:pk>/train/', views.project_train, name='project-train', kwargs={'sub_path': ''}),
    path('<int:pk>/store/', views.project_store, name='project-store', kwargs={'sub_path': ''}),
    path('<int:pk>/health/', views.project_health, name='project-health', kwargs={'sub_path': ''}),
    path('<int:pk>/settings/<sub_path>', views.project_settings, name='project-settings-anything'),
    path('<int:pk>/mce', core_views.fallback, name='project-settings-mce'),
    path('<int:pk>/editor-designer', core_views.fallback, name='project-settings-editor-designer'),
    path('<int:pk>/report', views.project_report, name='project-report'),
    path('<int:pk>/demo', core_views.fallback, name='project-demo'),
    path('upload-example/', views.upload_example_using_config, name='project-upload-example-using-config'),
]

# reverse for projects:api:name
_api_urlpatterns = [
    # CRUD
    path('', api.ProjectListAPI.as_view(), name='project-list'),
    path('list', api.ListProjectListAPI.as_view(), name='project-list-2'),
    path('admin/', api.ProjectListAdminViewAPI.as_view(), name='admin-project-list'),
    path('<int:pk>/', api.ProjectAPI.as_view(), name='project-detail'),
    path('<int:pk>/upload', api.ProjectUploadFileApi.as_view(), name='project-upload-file'),

    # Get next task
    path('<int:pk>/next/', api.ProjectNextTaskAPI.as_view(), name='project-next'),

    # Validate label config in general
    path('validate/', api.LabelConfigValidateAPI.as_view(), name='label-config-validate'),

    # Validate label config for project
    path('<int:pk>/validate/', api.ProjectLabelConfigValidateAPI.as_view(), name='project-label-config-validate'),

    # Project summary
    path('<int:pk>/summary/', api.ProjectSummaryAPI.as_view(), name='project-summary'),

    # Tasks list for the project: get and destroy
    path('<int:pk>/tasks/', api.ProjectTaskListAPI.as_view(), name='project-tasks-list'),

    # Generate sample task for this project
    path('<int:pk>/sample-task/', api.ProjectSampleTask.as_view(), name='project-sample-task'),

    # List available model versions
    path('<int:pk>/model-versions/', api.ProjectModelVersions.as_view(), name='project-model-versions'),

    # Get statistics for the project dataset
    path('<int:pk>/statistics/', api.ProjectStatisticsAPI.as_view(), name='project-statistics'),

    # Project docker management
    path('<int:pk>/docker/', api.ProjectDockerAPI.as_view(), name='project-docker'),
    path('<int:pk>/docker/images', api.ProjectDockerImageAPI.as_view(), name='project-docker-images'),
    path('<int:pk>/docker/<str:container_id>', api.ProjectDockerContainerAPI.as_view(), name='project-docker-container'),

    # Project tensorboar
    path('<int:pk>/tensorboard/', api.ProjectTensorboardAPI.as_view(), name='project-tensorboard'),

    # # Project logs
    # path('<int:pk>/logs/', api.ProjectLogsAPI.as_view(), name='project-logs'),
    # Project logs
    path('<int:pk>/logs/', api.ProjectLogsAPI.as_view(), name='project-logs'),
    path('<int:pk>/logs/upload', api.ProjectLogsUploadAPIView.as_view(), name='project-logs-upload'),
    path('<int:pk>/logs/download', api.ProjectLogsDownloadAPIView.as_view(), name='project-logs-download'),

    # Update project stats
    path('<int:pk>/stats/', api.ProjectStatsAPI.as_view(), name='project-stats'),

    # Get project report
    path('<int:pk>/report/', api.ProjectReportAPI.as_view(), name='project-report'),
    path('reset-ml-port/', api.ResetMLPortAPIView.as_view(), name='reset-ml-port'),
    path('get-ml-port/', api.GetMLPortAPIView.as_view(), name='reset-ml-port'),
    path('crawl-history/', api.CrawlHistoryAPI.as_view(), name='crawl-history'),
    # path('queue', api.ProjectCrawlQueueAPI.as_view(), name='project-queue'),
    # Update project gpu
    # path('<int:pk>/gpu/', api.ProjectGPUAPI.as_view(), name='project-gpu'),
    # Update project checkpoint
    # path('<int:pk>/checkpoint/', api.ProjectCheckpointAPI.as_view(), name='project-checkpoint'),
    # path('auto-api/', api.AutoAPI.as_view(), name='auto-api')
    path('labels/', api.ProjectLabelAPI.as_view(), name='project-label'),
    path('pii/', api.ProjectPiiAPI.as_view(), name='project-pii'),
]

# _api_urlpatterns_templates = [
#     path('', api.TemplateListAPI.as_view(), name='template-list'),
# ]
_api_urlpatterns_crawl = [
    path('', crawl_api.CrawlDataAPI.as_view(), name='crawl'),
]

_api_urlpatterns_computegpu = [
    path('', api.ComputeGPUAPI.as_view(), name='computeGPU'),
]

_url_reverse = [
    path('', api.ReverseURLAPI.as_view(), name='reverseURL'),
]

_url_setenv = [
    path('', api.SetEnvAPI.as_view(), name='SetEnvAPI'),
]

urlpatterns = [
    path('projects/', include(_urlpatterns)),
    path('create-project/', views.project_create, name='project-create'),
    path('api/projects/', include((_api_urlpatterns, app_name), namespace='api')),
    path('api/crawl', include((_api_urlpatterns_crawl, app_name), namespace='api-crawl')),
    path('api/compute_gpu', include((_api_urlpatterns_computegpu, app_name), namespace='api-compute')),
    # path('api/templates/', include((_api_urlpatterns_templates, app_name), namespace='api-templates')),
    re_path(r'^projects/[^/]+/import/', core_views.fallback, name='project-import'),
    path('api/reverse_url/', include(_url_reverse)),
    path('api/set_env/', include(_url_setenv)),
]
