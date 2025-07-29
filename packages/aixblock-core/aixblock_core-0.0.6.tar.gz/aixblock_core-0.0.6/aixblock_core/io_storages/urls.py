"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
from django.urls import path, include

from .s3.api import *
from .azure_blob.api import *
from .gcs.api import *
from .redis.api import *
from .localfiles.api import *
from .all_api import *
from .gdriver.api import *

app_name = 'storages'

# IO Storages CRUD
_api_urlpatterns = [
    # All storages
    path("", AllImportStorageListAPI.as_view(), name="storage-list"),
    path("global", AllGlobalStorageListAPI.as_view(), name="storage-list-global"),
    path("global/s3", S3ExportStorageListAPI.as_view(), name="storage-list-global-s3"),
    path('global/gcs', GCSExportStorageListAPI.as_view(), name='export-storage-global-gcs'),
    path('global/gdriver', GDriverExportStorageListAPI.as_view(), name='export-storage-global-gdriver'),
    path("global/redis", RedisExportStorageListAPI.as_view(), name="storage-list-global-redis"),
    path("global/azure", AzureBlobExportStorageListAPI.as_view(), name="storage-list-global-azure"),
    path("link-global/<int:pk>/<int:project>/<str:type>", AllGlobalStorageLinkAPI.as_view(), name="storage-list-global-link"),
    path("delete-global/<str:storage_type>/<int:pk>", AllGlobalStorageDeleteAPI.as_view(), name="storage-list-global-delete"),
    path("global/<str:storage_type>/<int:pk>", AllGlobalStorageEditAPI.as_view(), name="storage-list-global-edit"),
    path("export", AllExportStorageListAPI.as_view(), name="export-storage-list"),
    path("types", AllImportStorageTypesAPI.as_view(), name="storage-types"),
    path(
        "export/types", AllExportStorageTypesAPI.as_view(), name="export-storage-types"
    ),

    # # All storages
    # path("", AllImportStorageListAPI.as_view(), name="storage-list"),
    # path("export", AllExportStorageListAPI.as_view(), name="export-storage-list"),
    # path("types", AllImportStorageTypesAPI.as_view(), name="storage-types"),
    # path("export/types", AllExportStorageTypesAPI.as_view(), name="export-storage-types"),
    # path('', AllImportStorageListAPI.as_view(), name='storage-list'),
    # path('export', AllExportStorageListAPI.as_view(), name='export-storage-list'),
    # path('types', AllImportStorageTypesAPI.as_view(), name='storage-types'),
    # path('export/types', AllExportStorageTypesAPI.as_view(), name='export-storage-types'),
    # Amazon S3
    path('s3', S3ImportStorageListAPI.as_view(), name='storage-s3-list'),
    path('s3/<int:pk>', S3ImportStorageDetailAPI.as_view(), name='storage-s3-detail'),
    path('s3/<int:pk>/sync', S3ImportStorageSyncAPI.as_view(), name='storage-s3-sync'),
    path('s3/validate', S3ImportStorageValidateAPI.as_view(), name='storage-s3-validate'),
    path('s3/form', S3ImportStorageFormLayoutAPI.as_view(), name='storage-s3-form'),
    path('export/s3', S3ExportStorageListAPI.as_view(), name='export-storage-s3-list'),
    path('export/s3/<int:pk>', S3ExportStorageDetailAPI.as_view(), name='export-storage-s3-detail'),
    path('export/s3/<int:pk>/sync', S3ExportStorageSyncAPI.as_view(), name='export-storage-s3-sync'),
    path('export/s3/validate', S3ExportStorageValidateAPI.as_view(), name='export-storage-s3-validate'),
    path('export/s3/form', S3ExportStorageFormLayoutAPI.as_view(), name='export-storage-s3-form'),
    
    # Microsoft Azure
    path('azure', AzureBlobImportStorageListAPI.as_view(), name='storage-azure-list'),
    path('azure/<int:pk>', AzureBlobImportStorageDetailAPI.as_view(), name='storage-azure-detail'),
    path('azure/<int:pk>/sync', AzureBlobImportStorageSyncAPI.as_view(), name='storage-azure-sync'),
    path('azure/validate', AzureBlobImportStorageValidateAPI.as_view(), name='storage-azure-validate'),
    path('azure/form', AzureBlobImportStorageFormLayoutAPI.as_view(), name='storage-azure-form'),
    path('export/azure', AzureBlobExportStorageListAPI.as_view(), name='export-storage-azure-list'),
    path('export/azure/<int:pk>', AzureBlobExportStorageDetailAPI.as_view(), name='export-storage-azure-detail'),
    path('export/azure/<int:pk>/sync', AzureBlobExportStorageSyncAPI.as_view(), name='export-storage-azure-sync'),
    path('export/azure/validate', AzureBlobExportStorageValidateAPI.as_view(), name='export-storage-azure-validate'),
    path('export/azure/form', AzureBlobExportStorageFormLayoutAPI.as_view(), name='export-storage-azure-form'),
    # Google Cloud Storage
    path('gcs', GCSImportStorageListAPI.as_view(), name='storage-gcs-list'),
    path('gcs/<int:pk>', GCSImportStorageDetailAPI.as_view(), name='storage-gcs-detail'),
    path('gcs/<int:pk>/sync', GCSImportStorageSyncAPI.as_view(), name='storage-gcs-sync'),
    path('gcs/validate', GCSImportStorageValidateAPI.as_view(), name='storage-gcs-validate'),
    path('gcs/form', GCSImportStorageFormLayoutAPI.as_view(), name='storage-gcs-form'),
    path('export/gcs', GCSExportStorageListAPI.as_view(), name='export-storage-gcs-list'),
    path('export/gcs/<int:pk>', GCSExportStorageDetailAPI.as_view(), name='export-storage-gcs-detail'),
    path('export/gcs/<int:pk>/sync', GCSExportStorageSyncAPI.as_view(), name='export-storage-gcs-sync'),
    path('export/gcs/validate', GCSExportStorageValidateAPI.as_view(), name='export-storage-gcs-validate'),
    path('export/gcs/form', GCSExportStorageFormLayoutAPI.as_view(), name='export-storage-gcs-form'),
    # Redis DB
    path('redis', RedisImportStorageListAPI.as_view(), name='storage-redis-list'),
    path('redis/<int:pk>', RedisImportStorageDetailAPI.as_view(), name='storage-redis-detail'),
    path('redis/<int:pk>/sync', RedisImportStorageSyncAPI.as_view(), name='storage-redis-sync'),
    path('redis/validate', RedisImportStorageValidateAPI.as_view(), name='storage-redis-validate'),
    path('redis/form', RedisImportStorageFormLayoutAPI.as_view(), name='storage-redis-form'),
    path('export/redis', RedisExportStorageListAPI.as_view(), name='export-storage-redis-list'),
    path('export/redis/<int:pk>', RedisExportStorageDetailAPI.as_view(), name='export-storage-redis-detail'),
    path('export/redis/<int:pk>/sync', RedisExportStorageSyncAPI.as_view(), name='export-storage-redis-sync'),
    path('export/redis/validate', RedisExportStorageValidateAPI.as_view(), name='export-storage-redis-validate'),
    path('export/redis/form', RedisExportStorageFormLayoutAPI.as_view(), name='export-storage-redis-form'),
    # Google Driver Storage
    path('gdriver', GDriverImportStorageListAPI.as_view(), name='storage-gdriver-list'),
    path('gdriver/<int:pk>', GDriverImportStorageDetailAPI.as_view(), name='storage-gdriver-detail'),
    path('gdriver/<int:pk>/sync', GDriverImportStorageSyncAPI.as_view(), name='storage-gdriver-sync'),
    path('gdriver/validate', GDriverImportStorageValidateAPI.as_view(), name='storage-gdriver-validate'),
    path('gdriver/form', GDriverImportStorageFormLayoutAPI.as_view(), name='storage-gdriver-form'),
    path('export/gdriver', GDriverExportStorageListAPI.as_view(), name='export-storage-gdriver-list'),
    path('export/gdriver/<int:pk>', GDriverExportStorageDetailAPI.as_view(), name='export-storage-gdriver-detail'),
    path('export/gdriver/<int:pk>/sync', GDriverExportStorageSyncAPI.as_view(), name='export-storage-gdriver-sync'),
    path('export/gdriver/validate', GDriverExportStorageValidateAPI.as_view(), name='export-storage-gdriver-validate'),
    path('export/gdriver/form', GDriverExportStorageFormLayoutAPI.as_view(), name='export-storage-gdriver-form'),
]
if settings.ENABLE_LOCAL_FILES_STORAGE:
    _api_urlpatterns += [
        # Local files
        path('localfiles', LocalFilesImportStorageListAPI.as_view(), name='storage-localfiles-list'),
        path('localfiles/<int:pk>', LocalFilesImportStorageDetailAPI.as_view(), name='storage-localfiles-detail'),
        path('localfiles/<int:pk>/sync', LocalFilesImportStorageSyncAPI.as_view(), name='storage-localfiles-sync'),
        path('localfiles/validate', LocalFilesImportStorageValidateAPI.as_view(), name='storage-localfiles-validate'),
        path('localfiles/form', LocalFilesImportStorageFormLayoutAPI.as_view(), name='storage-localfiles-form'),
        path('export/localfiles', LocalFilesExportStorageListAPI.as_view(), name='export-storage-localfiles-list'),
        path(
            'export/localfiles/<int:pk>',
            LocalFilesExportStorageDetailAPI.as_view(),
            name='export-storage-localfiles-detail',
        ),
        path(
            'export/localfiles/<int:pk>/sync',
            LocalFilesExportStorageSyncAPI.as_view(),
            name='export-storage-localfiles-sync',
        ),
        path(
            'export/localfiles/validate',
            LocalFilesExportStorageValidateAPI.as_view(),
            name='export-storage-localfiles-validate',
        ),
        path(
            'export/localfiles/form',
            LocalFilesExportStorageFormLayoutAPI.as_view(),
            name='export-storage-localfiles-form',
        ),
    ]

urlpatterns = [
    path('api/storages/', include((_api_urlpatterns, app_name), namespace='api')),
]
