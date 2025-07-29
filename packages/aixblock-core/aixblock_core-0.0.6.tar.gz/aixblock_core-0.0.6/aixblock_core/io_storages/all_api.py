"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import logging

from django.conf import settings
from rest_framework import generics
from rest_framework.views import APIView
from core.permissions import all_permissions
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from aixblock_core.core.utils.common import load_func
from .azure_blob.serializers import AzureBlobImportStorageSerializer
from .gcs.serializers import GCSImportStorageSerializer
from .gdriver.serializers import GDriverImportStorageSerializer
from .localfiles.api import LocalFilesImportStorageListAPI, LocalFilesExportStorageListAPI

from .s3.models import S3ImportStorage
# from .localfiles.models import LocalFilesImportStorage
from .gdriver.models import GDriverImportStorage
from .gcs.models import  GCSImportStorage
from .redis.models import  RedisImportStorage
from .azure_blob.models import  AzureBlobImportStorage

from .s3.models import S3ExportStorage
# from .localfiles.models import LocalFilesExportStorage
from .gdriver.models import GDriverExportStorage
from .gcs.models import  GCSExportStorage
from .redis.models import  RedisExportStorage
from .azure_blob.models import  AzureBlobExportStorage
from projects.models import Project

from django.db.models import F, Value, CharField
from django.db.models.functions import Coalesce
from django.db.models import Q

logger = logging.getLogger(__name__)
# TODO: replace hardcoded apps lists with search over included storage apps


get_storage_list = load_func(settings.GET_STORAGE_LIST)


def _get_common_storage_list():
    storage_list = get_storage_list()
    # if settings.ENABLE_LOCAL_FILES_STORAGE:
    #     storage_list += [{
    #         'name': 'localfiles',
    #         'title': 'Local files',
    #         'import_list_api': LocalFilesImportStorageListAPI,
    #         'export_list_api': LocalFilesExportStorageListAPI
    #     }]

    return storage_list


_common_storage_list = _get_common_storage_list()


@method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['Storage'],
        operation_summary='List all import storages types',
        operation_description='Retrieve a list of the import storages types.',
        responses={"200": "A list of import storages types {'name': name, 'title': title}."}
    ))
class AllImportStorageTypesAPI(APIView):
    permission_required = all_permissions.projects_change

    def get(self, request, **kwargs):
        return Response([{'name': s['name'], 'title': s['title']} for s in _common_storage_list])


@method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['Storage'],
        operation_summary='List all export storages types',
        operation_description='Retrieve a list of the export storages types.',
        responses={"200": "A list of export storages types {'name': name, 'title': title}."}
    ))
class AllExportStorageTypesAPI(APIView):
    permission_required = all_permissions.projects_change

    def get(self, request, **kwargs):
        return Response([{'name': s['name'], 'title': s['title']} for s in _common_storage_list])


@method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['Storage'],
        operation_summary='List all import storages from the project',
        operation_description='Retrieve a list of the import storages of all types with their IDs.',
        manual_parameters=[
            openapi.Parameter(
                name='project',
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_PATH,
                description='A unique integer value identifying your project.'),
        ],
        responses={200: "List of ImportStorageSerializer"}
    ))
class AllImportStorageListAPI(generics.ListAPIView):

    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_required = all_permissions.projects_change

    def _get_response(self, api, request, *args, **kwargs):
        try:
            view = api.as_view()
            response = view(request._request, *args, **kwargs)
            payload = response.data
            if not isinstance(payload, list):
                raise ValueError(f'Response is not list')
            return response.data
        except Exception as exc:
            logger.error(f"Can't process {api.__class__.__name__}", exc_info=True)
            return []

    def list(self, request, *args, **kwargs):
        list_responses = sum([
            self._get_response(s['import_list_api'], request, *args, **kwargs) 
            for s in _common_storage_list
        ], [])
        return Response(list_responses)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["Storage"],
        operation_summary="List all import storages from the project",
        operation_description="Retrieve a list",
        manual_parameters=[
        ],
        responses={200: "List of ImportStorageSerializer"},
    ),
)
@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["Storage"],
        operation_summary="Add global storage",
        operation_description="""
    Add an global storage using the AiXBlock UI or by sending a POST request using the following cURL 
    command:
    ```bash
    curl -X POST -H 'Content-type: application/json' {host}/api/storages/global -H 'Authorization: Token abc123'\\
    --data '{{"url": "http://localhost:9090"}}' 
    """.format(
            host=(settings.HOSTNAME or "https://localhost:8080")
        ),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "project": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="Project ID"
                ),
                "url": openapi.Schema(
                    type=openapi.TYPE_STRING, description="ML backend URL"
                ),
            },
        ),
    ),
)
class AllGlobalStorageListAPI(generics.ListAPIView):

    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_required = all_permissions.projects_change

    def get_queryset(self):
        # Retrieve data from both models
        org_id = self.request.user.active_organization_id
        s3_import_storages = S3ImportStorage.objects.filter(is_global=True, org_id=org_id)
        azure_blob_import_storages = AzureBlobImportStorage.objects.filter(is_global=True, org_id=org_id)
        gdriver_import_storages = GDriverImportStorage.objects.filter(is_global=True, org_id=org_id)
        gcs_import_storages = GCSImportStorage.objects.filter(is_global=True, org_id=org_id)
        redis_import_storages = RedisImportStorage.objects.filter(is_global=True, org_id=org_id)

        # Convert to lists of tuples
        s3_import_storages_data = list(
            s3_import_storages.values_list(
                "id",
                "title", 
                "project_id", 
                "user_id", 
                "is_global", 
                "last_sync",
                "last_sync_count",
                "created_at",
                "bucket",
                "regex_filter",
                "aws_access_key_id",
                "aws_secret_access_key",
                "s3_endpoint",
                "region_name",
                "aws_session_token"
            ).order_by("-id")
        )
        azure_blob_import_storages_data = list(
            azure_blob_import_storages.values_list(
                "id",
                "title",
                "project_id",
                "user_id",
                "is_global",
                "last_sync",
                "last_sync_count",
                "created_at",
                "regex_filter",
                "container",
                "account_name"
            ).order_by("-id")
        )

        # Add placeholder value for 'bucket' in azure_blob_import_storages_data
        azure_blob_import_storages_data_with_bucket = [
            (
                id,
                title,
                project_id,
                user_id,
                is_global,
                last_sync,
                last_sync_count,
                created_at,
                None,
                "azure",
                regex_filter,
                None,
                None,
                container,
                account_name
            )
            for id, title, project_id, user_id,is_global, last_sync, last_sync_count, created_at,regex_filter, container, account_name in azure_blob_import_storages_data
        ]

        gdriver_import_storages_data = list(
            gdriver_import_storages.values_list(
                "id",
                "title",
                "project_id",
                "user_id",
                "is_global",
                "last_sync",
                "last_sync_count",
                "created_at",
                "regex_filter",
                "bucket"
            ).order_by("-id")
        )

        # Add placeholder value for 'bucket' in azure_blob_import_storages_data
        gdriver_import_storages_data_with_bucket = [
            (
                id,
                title,
                project_id,
                 user_id,
                is_global,
                last_sync,
                last_sync_count,
                created_at,
                bucket,
                "gdriver",
                regex_filter
            )
            for id, title, project_id, user_id,is_global, last_sync, last_sync_count, created_at, regex_filter, bucket in gdriver_import_storages_data
        ]

        gcs_import_storages_data = list(
            gcs_import_storages.values_list(
                "id",
                "title",
                "project_id",
                "user_id",
                "is_global",
                "last_sync",
                "last_sync_count",
                "created_at",
                "regex_filter",
                "bucket"
            ).order_by("-id")
        )

        # Add placeholder value for 'bucket' in azure_blob_import_storages_data
        gcs_import_storages_data_with_bucket = [
            (
                id,
                title,
                project_id,
                 user_id,
                is_global,
                last_sync,
                last_sync_count,
                created_at,
                bucket,
                "gcs",
                regex_filter
            )
            for id, title, project_id, user_id,is_global, last_sync, last_sync_count, created_at,regex_filter, bucket in gcs_import_storages_data
        ]

        redis_import_storages_data = list(
            redis_import_storages.values_list(
                "id",
                "title",
                "project_id",
                "user_id",
                "is_global",
                "last_sync",
                "last_sync_count",
                "created_at",
                "regex_filter"
            ).order_by("-id")
        )

        # Add placeholder value for 'bucket' in azure_blob_import_storages_data
        redis_import_storages_data_with_bucket = [
            (
                id,
                title,
                project_id,
                 user_id,
                is_global,
                last_sync,
                last_sync_count,
                created_at,
                None,
                "redis",
                regex_filter
            )
            for id, title, project_id, user_id,is_global, last_sync, last_sync_count, created_at,regex_filter in redis_import_storages_data
        ]

        # Add storage type to S3 data
        s3_import_storages_data_with_type = [
            (
                id,
                title,
                project_id,
                user_id,
                is_global,
                last_sync,
                last_sync_count,
                created_at,
                bucket,
                "s3",
                regex_filter,
                # "",
                # "",
                s3_endpoint,
                region_name,
                # aws_session_token
            )
            for id, title, project_id,user_id,is_global, last_sync, last_sync_count, created_at, bucket,regex_filter,aws_access_key_id,aws_secret_access_key,s3_endpoint,region_name,aws_session_token in s3_import_storages_data
        ]

        # Combine querysets using union
        combined_data = (
            s3_import_storages_data_with_type
            + azure_blob_import_storages_data_with_bucket
            + gdriver_import_storages_data_with_bucket
            + gcs_import_storages_data_with_bucket
            + redis_import_storages_data_with_bucket
        )
        return combined_data

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Convert the combined data to a list of dictionaries
        combined_data = [
            dict(
                zip(
                    [
                        "id",
                        "title",
                        "project_id",
                        "user_id",
                        "is_global",
                        "last_sync",
                        "last_sync_count",
                        "created_at",
                        "bucket",
                        "storage_type",
                        "regex_filter",
                        # "aws_access_key_id",
                        # "aws_secret_access_key",
                        "s3_endpoint",
                        "region_name",
                        "container",
                        "account_name"
                        # "account_key",
                        # "path",
                        # "host",
                        # "port",
                        # "password",
                        # "prefix",
                        # "google_application_credentials"
                    ],
                    row,
                )
            )
            for row in queryset
        ]
        return Response(combined_data)
    # def post(self, request, *args, **kwargs):
    #     return super(S3ImportStorage, self).post(request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        print(request.query_params.get('storage_type'))
        # storage = self.get_object()
        # check connectivity & access, raise an exception if not satisfied
        # storage.validate_connection()
        # storage.sync()
        # storage.refresh_from_db()
        # if request.query_params.get('storage_type', "") == "s3":
        #     return super(S3ImportStorage, self).post(request, *args, **kwargs)
        # elif request.query_params.get('storage_type', "") == "azure":
        #     return super(AzureBlobImportStorage, self).post(request, *args, **kwargs)
        # elif request.query_params.get('storage_type', "") == "redis":
        #     return super(RedisImportStorage, self).post(request, *args, **kwargs)
        # elif request.query_params.get('storage_type', "") == "gdriver":
        #     return super(GDriverImportStorage, self).post(request, *args, **kwargs)
        # elif request.query_params.get('storage_type', "") == "gcs":
        #     return super(GCSImportStorage, self).post(request, *args, **kwargs)

@method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['Storage'],
        operation_summary='List all export storages from the project',
        operation_description='Retrieve a list of the export storages of all types with their IDs.',
        manual_parameters=[
            openapi.Parameter(
                name='project',
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_PATH,
                description='A unique integer value identifying your project.'),
        ],
        responses={200: "List of ExportStorageSerializer"}
    ))
class AllGlobalStorageAPI(generics.ListAPIView):

    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_required = all_permissions.projects_change

    def get_queryset(self):
        # Retrieve data from both models
        org_id = self.request.user.active_organization_id
        s3_import_storages = S3ImportStorage.objects.filter(is_global=True, org_id=org_id)
        azure_blob_import_storages = AzureBlobImportStorage.objects.filter(is_global=True, org_id=org_id)
        gdriver_import_storages = GDriverImportStorage.objects.filter(is_global=True, org_id=org_id)
        gcs_import_storages = GCSImportStorage.objects.filter(is_global=True, org_id=org_id)
        redis_import_storages = RedisImportStorage.objects.filter(is_global=True, org_id=org_id)

        # Convert to lists of tuples
        s3_import_storages_data = list(
            s3_import_storages.values_list(
                "id","title", "project_id", "user_id", "is_global",  "last_sync", "last_sync_count",'created_at', "bucket","regex_filter","aws_access_key_id","aws_secret_access_key","s3_endpoint","region_name"
            )
        )
        azure_blob_import_storages_data = list(
            azure_blob_import_storages.values_list(
                "id",
                "title",
                "project_id",
                "user_id",
                "is_global",
                "last_sync",
                "last_sync_count",
                "created_at",
                "regex_filter"
            )
        )

        # Add placeholder value for 'bucket' in azure_blob_import_storages_data
        azure_blob_import_storages_data_with_bucket = [
            (
                id,
                title,
                project_id,
                 user_id,
                is_global,
                last_sync,
                last_sync_count,
                created_at,
                None,
                "azure",
                regex_filter,
                None,
                None,
                None
            )
            for id, title, project_id, user_id,is_global, last_sync, last_sync_count, created_at,regex_filter in azure_blob_import_storages_data
        ]

        gdriver_import_storages_data = list(
            gdriver_import_storages.values_list(
                "id",
                "title",
                "project_id",
                "user_id",
                "is_global",
                "last_sync",
                "last_sync_count",
                "created_at",
                "regex_filter"
            )
        )

        # Add placeholder value for 'bucket' in azure_blob_import_storages_data
        gdriver_import_storages_data_with_bucket = [
            (
                id,
                title,
                project_id,
                 user_id,
                is_global,
                last_sync,
                last_sync_count,
                created_at,
                None,
                "gdriver",
                regex_filter,
                None,
                None,
                None,
                None,
                None,
                "path",
                None,
                None,
                None,
                "prefix",
                "google_application_credentials",
            )
            for id, title, project_id, user_id,is_global, last_sync, last_sync_count, created_at,regex_filter in gdriver_import_storages_data
        ]

        gcs_import_storages_data = list(
            gcs_import_storages.values_list(
                "id",
                "title",
                "project_id",
                "user_id",
                "is_global",
                "last_sync",
                "last_sync_count",
                "created_at",
                "regex_filter"
            )
        )

        # Add placeholder value for 'bucket' in azure_blob_import_storages_data
        gcs_import_storages_data_with_bucket = [
            (
                id,
                title,
                project_id,
                 user_id,
                is_global,
                last_sync,
                last_sync_count,
                created_at,
                None,
                "gcs",
                regex_filter,
                None,
                None,
                None,
                None,
                None,
                "path",
                None,
                None,
                None,
                "prefix",
                "google_application_credentials",
            )
            for id, title, project_id, user_id,is_global, last_sync, last_sync_count, created_at,regex_filter in gcs_import_storages_data
        ]

        redis_import_storages_data = list(
            redis_import_storages.values_list(
                "id",
                "title",
                "project_id",
                "user_id",
                "is_global",
                "last_sync",
                "last_sync_count",
                "created_at",
                "regex_filter"
            )
        )

        # Add placeholder value for 'bucket' in azure_blob_import_storages_data
        redis_import_storages_data_with_bucket = [
            (
                id,
                title,
                project_id,
                 user_id,
                is_global,
                last_sync,
                last_sync_count,
                created_at,
                None,
                "redis",
                regex_filter,
                None,
                None,
                None,
                None,
                None,
                "path",
                "host",
                "port",
                "password",
                None,
                None,
            )
            for id, title, project_id, user_id,is_global, last_sync, last_sync_count, created_at,regex_filter in redis_import_storages_data
        ]

        # Add storage type to S3 data
        s3_import_storages_data_with_type = [
            (
                id,
                title,
                project_id,
                user_id,
                is_global,
                last_sync,
                last_sync_count,
                created_at,
                bucket,
                "s3",
                regex_filter,
                aws_access_key_id,
                aws_secret_access_key,
                s3_endpoint,
                region_name,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None
            )
            for id, title, project_id,user_id,is_global, last_sync, last_sync_count, created_at, bucket,regex_filter,aws_access_key_id,aws_secret_access_key,s3_endpoint,region_name in s3_import_storages_data
        ]

        # Combine querysets using union
        combined_data = (
            s3_import_storages_data_with_type
            + azure_blob_import_storages_data_with_bucket
            + gdriver_import_storages_data_with_bucket
            + gcs_import_storages_data_with_bucket
            + redis_import_storages_data_with_bucket
        )
        return combined_data

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Convert the combined data to a list of dictionaries
        combined_data = [
            dict(
                zip(
                    [
                        "id",
                        "title",
                        "project_id",
                        "user_id",
                        "is_global",
                        "last_sync",
                        "last_sync_count",
                        "created_at",
                        "bucket",
                        "storage_type",
                        "regex_filter",
                        "aws_access_key_id",
                        "aws_secret_access_key",
                        "s3_endpoint",
                        "region_name",
                        "account_name",
                        "account_key",
                        "path",
                        "host",
                        "port",
                        "password",
                        "prefix",
                        "google_application_credentials"
                    ],
                    row,
                )
            )
            for row in queryset
        ]
        return Response(combined_data)
    # def post(self, request, *args, **kwargs):
    #     return super(S3ImportStorage, self).post(request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        print(request.query_params.get('storage_type'))
        # storage = self.get_object()
        # check connectivity & access, raise an exception if not satisfied
        # storage.validate_connection()
        # storage.sync()
        # storage.refresh_from_db()
        # if request.query_params.get('storage_type', "") == "s3":
        #     return super(S3ImportStorage, self).post(request, *args, **kwargs)
        # elif request.query_params.get('storage_type', "") == "azure":
        #     return super(AzureBlobImportStorage, self).post(request, *args, **kwargs)
        # elif request.query_params.get('storage_type', "") == "redis":
        #     return super(RedisImportStorage, self).post(request, *args, **kwargs)
        # elif request.query_params.get('storage_type', "") == "gdriver":
        #     return super(GDriverImportStorage, self).post(request, *args, **kwargs)
        # elif request.query_params.get('storage_type', "") == "gcs":
        #     return super(GCSImportStorage, self).post(request, *args, **kwargs)

@method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['Storage'],
        operation_summary='List all export storages from the project',
        operation_description='Retrieve a list of the export storages of all types with their IDs.',
        manual_parameters=[
            openapi.Parameter(
                name='project',
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_PATH,
                description='A unique integer value identifying your project.'),
        ],
        responses={200: "List of ExportStorageSerializer"}
    ))
class AllExportStorageListAPI(generics.ListAPIView):

    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_required = all_permissions.projects_change

    def _get_response(self, api, request, *args, **kwargs):
        view = api.as_view()
        response = view(request._request, *args, **kwargs)
        return response.data

    def list(self, request, *args, **kwargs):
        list_responses = sum([
            self._get_response(s['export_list_api'], request, *args, **kwargs) for s in _common_storage_list], [])
        return Response(list_responses)
class AllGlobalStorageLinkAPI(generics.ListAPIView):

    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_required = all_permissions.projects_change
    def get(self, request, *args, **kwargs):
        print(kwargs)
        print(kwargs.get("pk"))
        print(kwargs.get("type"))
        pass
       
    # def post(self, request, *args, **kwargs):
    #     return super(S3ImportStorage, self).post(request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        # print(request.data)
        print(kwargs)
        print(kwargs.get("pk"))
        print(kwargs.get("type"))

        try:
            project = Project.objects.filter(id=kwargs.get("pk")).first()
            data_type =  project.data_types
            if 'image' in data_type:
                regex_filter = f"raw_files_{project.pk}/.+\.(jpg|png|jpeg|gif|webp|svg)"
            elif 'audio' in data_type:
                regex_filter = f"raw_files_{project.pk}/.+\.(mp3|ogg|wav|m4a|m4b|aiff|au|flac)"
            elif 'video' in data_type:
                regex_filter = f"raw_files_{project.pk}/.+\.(mp4|h264|webm|webm)"
            else:
                regex_filter = f"raw_files_{project.pk}/.+\.(txt|csv|json|tsv)"
        except Exception as e:
            print(e)
            regex_filter = ""

        if kwargs.get('type') == "s3":
            item = S3ImportStorage.objects.filter(pk=kwargs.get("project")).first()

            if item.regex_filter and item.regex_filter != "":
                regex_filter = item.regex_filter

            export_storage = S3ExportStorage(
                project_id=kwargs.get('pk'),
                title=f"{item.title} (Linked with #{item.pk})",
                bucket=item.bucket,
                prefix=item.prefix,
                aws_access_key_id = item.aws_access_key_id,
                aws_secret_access_key = item.aws_secret_access_key,
                s3_endpoint = item.s3_endpoint,
                aws_session_token = item.aws_session_token,
                regex_filter=regex_filter,
                use_blob_urls=item.use_blob_urls,
                region_name=item.region_name # kwargs.get('region'),
            )

            # export_storage = S3ExportStorage.objects.create(
            #     project_id=kwargs.get('pk'),
            #     bucket=kwargs.get('path'),
            #     prefix=kwargs.get('prefix'),
            #     regex_filter=kwargs.get('regex', filter_s3),
            #     use_blob_urls=True,
            #     region_name=kwargs.get('region'),
            # )
            
            storage = S3ImportStorage(export_storage=export_storage.id,title=f"{item.title} (Linked with #{item.pk})",bucket=item.bucket, aws_access_key_id = item.aws_access_key_id,
                                                     aws_secret_access_key = item.aws_secret_access_key, s3_endpoint = item.s3_endpoint, region_name = item.region_name,
                                                     aws_session_token = item.aws_session_token, use_blob_urls=True, regex_filter=regex_filter,
                                                     is_global=False,user_id=self.request.user.id,org_id=self.request.user.active_organization_id,
                                                     project_id=kwargs.get('pk'))
            storage.validate_connection()
            export_storage.save()
            storage.export_storage=export_storage.id
            storage.save()
            storage.refresh_from_db()
            storage.create_folder(f"raw_files_{kwargs.get('pk')}")
            return Response(status=200)
        elif kwargs.get('type', "") == "azure":
            item = AzureBlobImportStorage.objects.filter(pk=kwargs.get("project")).first()

            if item.regex_filter and item.regex_filter != "":
                regex_filter = item.regex_filter

            export_storage = AzureBlobExportStorage.objects.create(
                project_id=kwargs.get('pk'),
                title=f"{item.title} (Linked with #{item.pk})",
                container=item.container,
                prefix=item.prefix,
                regex_filter=regex_filter,
                use_blob_urls=True,
                account_name = item.account_name,
                account_key = item.account_key
            )
            # export_storage = AzureBlobExportStorage.objects.create(
            #     project_id=kwargs.get('pk'),
            #     container=kwargs.get('path'),
            #     prefix=kwargs.get('prefix'),
            #     regex_filter=kwargs.get('regex', regex_filter),
            #     use_blob_urls=True,
            #     account_name = kwargs.get('account_name'),
            #     account_key = kwargs.get('account_key')
            # )
            storage = AzureBlobImportStorage.objects.create(
                export_storage=export_storage.id,
                # project_id=kwargs.get('pk'),
                title=f"{item.title} (Linked with #{item.pk})",
                container=item.container,
                prefix=item.prefix,
                regex_filter=regex_filter,
                account_name = item.account_name,
                account_key = item.account_key,
                use_blob_urls=True,is_global=False,
                user_id=self.request.user.id,
                org_id=self.request.user.active_organization_id,project_id=kwargs.get('pk')
            )
            storage.validate_connection()
            storage.refresh_from_db()
            storage.create_folder(f"raw_files_{kwargs.get('pk')}")
            return Response(status=200)
        elif kwargs.get('type', "") == "redis":
            item =  RedisImportStorage.objects.filter(id=kwargs.get("project")).first()
            export_storage = RedisExportStorage.objects.create(
                project_id=kwargs.get('pk'),
                title=f"{item.title} (Linked with #{item.pk})",
                host=item.host,
                port=item.port,
                password=item.password
            )
            storage = RedisImportStorage.objects.create(
                export_storage=export_storage.id,
                title=f"{item.title} (Linked with #{item.pk})",
                # project_id=kwargs.get('pk'),
                path=kwargs.get('path'),
                host=item.host,
                port=item.port,
                password=item.password,is_global=False,user_id=self.request.user.id,org_id=self.request.user.active_organization_id,
                project_id=kwargs.get('pk')
            )
            storage.validate_connection()
            storage.refresh_from_db()
            storage.create_folder(f"raw_files_{kwargs.get('pk')}")
            return Response(status=200)
        elif kwargs.get('type', "") == "gdriver":
            item = GDriverImportStorage.objects.filter(id=kwargs.get("project")).first()

            if item.regex_filter and item.regex_filter != "":
                regex_filter = item.regex_filter

            export_storage = GDriverExportStorage.objects.create(
                project_id=kwargs.get('pk'),
                title=f"{item.title} (Linked with #{item.pk})",
                bucket=item.bucket,
                prefix=item.prefix,
                regex_filter=regex_filter,
                google_application_credentials=item.google_application_credentials,
               use_blob_urls=True
                )
            storage = GDriverImportStorage.objects.create(
                export_storage=export_storage.id,
                # project_id=kwargs.get('pk'),
                title=f"{item.title} (Linked with #{item.pk})",
                bucket=item.bucket,
                prefix=item.prefix,
                regex_filter=regex_filter,
                google_application_credentials=item.google_application_credentials,
                use_blob_urls=True,is_global=False,user_id=self.request.user.id,org_id=self.request.user.active_organization_id,
                project_id=kwargs.get('pk')
            )
            storage.validate_connection()
            storage.refresh_from_db()
            storage.create_folder(f"raw_files_{kwargs.get('pk')}")
            return Response(status=200)
        elif kwargs.get('type', "") == "gcs":
            item = GCSImportStorage.objects.filter(id=kwargs.get("project")).first()

            if item.regex_filter and item.regex_filter != "":
                regex_filter = item.regex_filter

            export_storage = GCSExportStorage.objects.create(
                project_id=kwargs.get('pk'),
                title=f"{item.title} (Linked with #{item.pk})",
                bucket=item.bucket,
                prefix=item.prefix,
                regex_filter=regex_filter,
                google_application_credentials=item.google_application_credentials,
                use_blob_urls=True
            )
            storage = GCSImportStorage.objects.create(
                export_storage=export_storage.id,
                # project_id=kwargs.get('pk'),
                title=f"{item.title} (Linked with #{item.pk})",
                bucket=item.bucket,
                prefix=item.prefix,
                regex_filter=regex_filter,
                google_application_credentials=item.google_application_credentials,
                use_blob_urls=True,is_global=False,user_id=self.request.user.id,org_id=self.request.user.active_organization_id,
                project_id=kwargs.get('pk')
            )
            storage.validate_connection()
            storage.refresh_from_db()
            storage.create_folder(f"raw_files_{kwargs.get('pk')}")
            return Response(status=200)
       
class AllGlobalStorageDeleteAPI(generics.ListAPIView):

    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_required = all_permissions.projects_change
    def delete(self, request, *args, **kwargs):
        # print(kwargs)
        # print(request)
        if kwargs.get('storage_type', "") == "s3":
            item = S3ImportStorage.objects.filter(id=kwargs.get("pk")).first()
            
            if item.user_id != request.user.id and not request.user.is_superuser:
                return Response({"message": "You do not have permission to delete this storage"}, status=403)
            
            item.delete()
            return Response(status=200)
        elif kwargs.get('storage_type', "") == "azure":
            item = AzureBlobImportStorage.objects.filter(id=kwargs.get('pk')).first()

            if item.user_id != request.user.id and not request.user.is_superuser:
                return Response({"message": "You do not have permission to delete this storage"}, status=403)
            
            item.delete()
            return Response(status=200)
        elif kwargs.get('storage_type', "") == "redis":
            item = RedisImportStorage.objects.filter(id=kwargs.get('pk')).first()

            if item.user_id != request.user.id and not request.user.is_superuser:
                return Response({"message": "You do not have permission to delete this storage"}, status=403)
            
            item.delete()
            return Response(status=200)
        elif kwargs.get('storage_type', "") == "gdriver":
            item = GDriverImportStorage.objects.filter(id=kwargs.get('pk')).first()

            if item.user_id != request.user.id and not request.user.is_superuser:
                return Response({"message": "You do not have permission to delete this storage"}, status=403)
            
            item.delete()
            return Response(status=200)
        elif kwargs.get('storage_type', "") == "gcs":
            item = GCSImportStorage.objects.filter(id=kwargs.get('pk')).first()

            if item.user_id != request.user.id and not request.user.is_superuser:
                return Response({"message": "You do not have permission to delete this storage"}, status=403)
            
            item.delete()
            return Response(status=200)
class AllGlobalStorageEditAPI(generics.ListAPIView):

    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_required = all_permissions.projects_change
    def get(self, request, *args, **kwargs):
        print(kwargs)
        print(kwargs.get("pk"))
        print(kwargs.get("storage_type"))
        pass
       
    # def post(self, request, *args, **kwargs):
    #     return super(S3ImportStorage, self).post(request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        # print(request.data)
        print(kwargs)
        print(kwargs.get("pk"))
        print(kwargs.get("storage_type"))
        import json
        dp = json.dumps(request.data)
        payload = json.loads(dp)
        try:
            project = Project.objects.filter(id=kwargs.get("pk")).first()
            data_type =  project.data_types
            if 'image' in data_type:
                regex_filter = f"raw_files_{project.pk}/.+\.(jpg|png|jpeg|gif|webp|svg)"
            elif 'audio' in data_type:
                regex_filter = f"raw_files_{project.pk}/.+\.(mp3|ogg|wav|m4a|m4b|aiff|au|flac)"
            elif 'video' in data_type:
                regex_filter = f"raw_files_{project.pk}/.+\.(mp4|h264|webm|webm)"
            else:
                regex_filter = f"raw_files_{project.pk}/.+\.(txt|csv|json|tsv)"
        except Exception as e:
            print(e)
            regex_filter = ""

        if kwargs.get('storage_type') == "s3":
            item = S3ImportStorage.objects.filter(pk=kwargs.get("pk")).first()

            if item.regex_filter or item.regex_filter != "":
                regex_filter = item.regex_filter

            item.bucket=payload['bucket']
            item.aws_access_key_id = payload['aws_access_key_id'] if 'aws_access_key_id' in payload and payload['aws_access_key_id'] else item.aws_access_key_id
            item.aws_secret_access_key = payload['aws_secret_access_key'] if 'aws_secret_access_key' in payload and payload['aws_secret_access_key'] else item.aws_secret_access_key
            item.s3_endpoint = payload['s3_endpoint'] if 's3_endpoint' in payload and payload['s3_endpoint'] else item.s3_endpoint
            item.region_name = payload['region_name'] if 'region_name' in payload and payload['region_name'] else item.region_name
            if 'aws_session_token' in payload:
                item.aws_session_token = payload['aws_session_token']
            else:
                item.aws_session_token = item.aws_session_token

            item.use_blob_urls = payload['use_blob_urls']
            
            item.regex_filter=regex_filter
            item.validate_connection()
            item.save()
            item.refresh_from_db()
     
            return Response(status=200)
        elif kwargs.get('storage_type', "") == "azure":
            storage = AzureBlobImportStorage.objects.filter(pk=kwargs.get("pk")).first()

            if storage.regex_filter or storage.regex_filter != "":
                regex_filter = storage.regex_filter


            storage.container=payload['container']
            storage.prefix=payload['prefix']
            storage.regex_filter=regex_filter
            storage.account_name = payload['account_name']
            storage.account_key = payload['account_key'] if "account_key" in payload and payload['account_key'] else storage.account_key
            storage.use_blob_urls= payload['use_blob_urls']
              
            storage.validate_connection()
            storage.save()
            storage.refresh_from_db()
            return Response(status=200)
        elif kwargs.get('storage_type', "") == "redis":
            storage =  RedisImportStorage.objects.filter(id=kwargs.get("pk")).first()
           
       
            storage.path=payload['path']
            storage.host=payload['host']
            storage.port=payload['port']
            storage.password=payload['password']
       
            storage.validate_connection()
            storage.refresh_from_db()
        
            return Response(status=200)
        elif kwargs.get('storage_type', "") == "gdriver":
            storage = GDriverImportStorage.objects.filter(id=kwargs.get("pk")).first()

            if storage.regex_filter or storage.regex_filter != "":
                regex_filter = storage.regex_filter

            storage.bucket=payload["bucket"]
            storage.prefix=payload['prefix']
            storage.regex_filter=regex_filter
            storage.google_application_credentials=payload['google_application_credentials'] if "google_application_credentials" in payload and payload['google_application_credentials'] else storage.google_application_credentials
            storage.use_blob_urls=kwargs.get('use_blob_urls', "") 
                
            storage.validate_connection()
            storage.refresh_from_db()
       
            return Response(status=200)
        elif kwargs.get('storage_type', "") == "gcs":
            storage = GCSImportStorage.objects.filter(id=kwargs.get("pk")).first()

            if storage.regex_filter or storage.regex_filter != "":
                regex_filter = storage.regex_filter

            storage.bucket=payload["bucket"]
            storage.prefix=payload['prefix']
            storage.regex_filter=regex_filter
            storage.google_application_credentials=payload['google_application_credentials'] if "google_application_credentials" in payload and payload['google_application_credentials'] else storage.google_application_credentials

            storage.validate_connection()
            storage.refresh_from_db()
     
            return Response(status=200)
    # def post(self, request, *args, **kwargs):
    #     print(request.query_params.get('storage_type'))
    #     storage = self.get_object()
    #     # check connectivity & access, raise an exception if not satisfied
    #     storage.validate_connection()
    #     storage.sync()
    #     storage.refresh_from_db()
    #     if request.query_params.get('storage_type', "") == "s3":
    #         return super(S3ImportStorage, self).post(request, *args, **kwargs)
    #     elif request.query_params.get('storage_type', "") == "azure":
    #         return super(AzureBlobImportStorage, self).post(request, *args, **kwargs)
    #     elif request.query_params.get('storage_type', "") == "redis":
    #         return super(RedisImportStorage, self).post(request, *args, **kwargs)
    #     elif request.query_params.get('storage_type', "") == "gdriver":
    #         return super(GDriverImportStorage, self).post(request, *args, **kwargs)
    #     elif request.query_params.get('storage_type', "") == "gcs":
    #         return super(GCSImportStorage, self).post(request, *args, **kwargs)
    #     elif request.query_params.get('storage_type', "") == "gdriver":
    #         return super(GDriverImportStorage, self).post(request, *args, **kwargs)
    #     storage.validate_connection()
    #     storage.refresh_from_db()
     
    #     return Response(status=200)