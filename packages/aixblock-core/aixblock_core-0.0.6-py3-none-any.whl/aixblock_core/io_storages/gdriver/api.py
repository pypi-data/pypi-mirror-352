"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi as openapi
from io_storages.gdriver.models import GDriverImportStorage, GDriverExportStorage
from io_storages.gdriver.serializers import GDriverImportStorageSerializer, GDriverExportStorageSerializer
from io_storages.api import (
    ImportStorageListAPI,
    ImportStorageDetailAPI,
    ImportStorageSyncAPI,
    ExportStorageListAPI,
    ExportStorageDetailAPI,
    ExportStorageSyncAPI,
    ImportStorageValidateAPI,
    ExportStorageValidateAPI,
    ImportStorageFormLayoutAPI,
    ExportStorageFormLayoutAPI,
)


@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=['Storage: GDriver'],
        operation_summary='Get all import storage',
        operation_description='Get a list of all GDriver import storage connections.',
        manual_parameters=[
            openapi.Parameter(
                name='project',
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_QUERY,
                description='Project ID',
            ),
        ],
    ),
)
@method_decorator(
    name='post',
    decorator=swagger_auto_schema(
        tags=['Storage: GDriver'],
        operation_summary='Create import storage',
        operation_description='Create a new GDriver import storage connection.',
    ),
)
class GDriverImportStorageListAPI(ImportStorageListAPI):
    queryset = GDriverImportStorage.objects.all()
    serializer_class = GDriverImportStorageSerializer


@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=['Storage: GDriver'],
        operation_summary='Get import storage',
        operation_description='Get a specific GDriver import storage connection.',
    ),
)
@method_decorator(
    name='patch',
    decorator=swagger_auto_schema(
        tags=['Storage: GDriver'],
        operation_summary='Update import storage',
        operation_description='Update a specific GDriver import storage connection.',
    ),
)
@method_decorator(
    name='delete',
    decorator=swagger_auto_schema(
        tags=['Storage: GDriver'],
        operation_summary='Delete import storage',
        operation_description='Delete a specific GDriver import storage connection.',
    ),
)
class GDriverImportStorageDetailAPI(ImportStorageDetailAPI):
    queryset = GDriverImportStorage.objects.all()
    serializer_class = GDriverImportStorageSerializer

    def delete(self, request, *args, **kwargs):
        import_id = kwargs.get("pk")
        import_intance = GDriverImportStorage.objects.filter(id=import_id).first()
        GDriverExportStorage.objects.filter(id=import_intance.export_storage).delete()

        return super(GDriverImportStorageDetailAPI, self).delete(request, *args, **kwargs)


@method_decorator(
    name='post',
    decorator=swagger_auto_schema(
        tags=['Storage: GDriver'],
        operation_summary='Sync import storage',
        operation_description='Sync tasks from an GDriver import storage connection.',
    ),
)
class GDriverImportStorageSyncAPI(ImportStorageSyncAPI):
    serializer_class = GDriverImportStorageSerializer


@method_decorator(
    name='post',
    decorator=swagger_auto_schema(
        tags=['Storage: GDriver'],
        operation_summary='Sync export storage',
        operation_description='Sync tasks from an GDriver export storage connection.',
    ),
)
class GDriverExportStorageSyncAPI(ExportStorageSyncAPI):
    serializer_class = GDriverExportStorageSerializer


@method_decorator(
    name='post',
    decorator=swagger_auto_schema(
        tags=['Storage: GDriver'],
        operation_summary='Validate import storage',
        operation_description='Validate a specific GDriver import storage connection.',
    ),
)
class GDriverImportStorageValidateAPI(ImportStorageValidateAPI):
    serializer_class = GDriverImportStorageSerializer


@method_decorator(
    name='post',
    decorator=swagger_auto_schema(
        tags=['Storage: GDriver'],
        operation_summary='Validate export storage',
        operation_description='Validate a specific GDriver export storage connection.',
    ),
)
class GDriverExportStorageValidateAPI(ExportStorageValidateAPI):
    serializer_class = GDriverExportStorageSerializer


@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=['Storage: GDriver'],
        operation_summary='Get all export storage',
        operation_description='Get a list of all GDriver export storage connections.',
        manual_parameters=[
            openapi.Parameter(
                name='project',
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_QUERY,
                description='Project ID',
            ),
        ],
    ),
)
@method_decorator(
    name='post',
    decorator=swagger_auto_schema(
        tags=['Storage: GDriver'],
        operation_summary='Create export storage',
        operation_description='Create a new GDriver export storage connection to store annotations.',
    ),
)
class GDriverExportStorageListAPI(ExportStorageListAPI):
    queryset = GDriverExportStorage.objects.all()
    serializer_class = GDriverExportStorageSerializer


@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=['Storage: GDriver'],
        operation_summary='Get export storage',
        operation_description='Get a specific GDriver export storage connection.',
    ),
)
@method_decorator(
    name='patch',
    decorator=swagger_auto_schema(
        tags=['Storage: GDriver'],
        operation_summary='Update export storage',
        operation_description='Update a specific GDriver export storage connection.',
    ),
)
@method_decorator(
    name='delete',
    decorator=swagger_auto_schema(
        tags=['Storage: GDriver'],
        operation_summary='Delete export storage',
        operation_description='Delete a specific GDriver export storage connection.',
    ),
)
class GDriverExportStorageDetailAPI(ExportStorageDetailAPI):
    queryset = GDriverExportStorage.objects.all()
    serializer_class = GDriverExportStorageSerializer


class GDriverImportStorageFormLayoutAPI(ImportStorageFormLayoutAPI):
    pass


class GDriverExportStorageFormLayoutAPI(ExportStorageFormLayoutAPI):
    pass
