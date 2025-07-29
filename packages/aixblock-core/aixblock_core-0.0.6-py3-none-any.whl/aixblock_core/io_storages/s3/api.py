"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi as openapi

from io_storages.s3.models import S3ImportStorage, S3ExportStorage
from io_storages.s3.serializers import S3ImportStorageSerializer, S3ExportStorageSerializer
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

from rest_framework import status, generics
from rest_framework.response import Response
from io_storages.s3.storage_server import S3Server

@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=['Storage:S3'],
        operation_summary='Get import storage',
        operation_description='Get a list of all S3 import storage connections.',
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
        tags=['Storage:S3'], operation_summary='Create new storage', operation_description='Get new S3 import storage'
    ),
)
class S3ImportStorageListAPI(ImportStorageListAPI):
    queryset = S3ImportStorage.objects.all()
    serializer_class = S3ImportStorageSerializer


@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=['Storage:S3'],
        operation_summary='Get import storage',
        operation_description='Get a specific S3 import storage connection.',
    ),
)
@method_decorator(
    name='patch',
    decorator=swagger_auto_schema(
        tags=['Storage:S3'],
        operation_summary='Update import storage',
        operation_description='Update a specific S3 import storage connection.',
    ),
)
@method_decorator(
    name='delete',
    decorator=swagger_auto_schema(
        tags=['Storage:S3'],
        operation_summary='Delete import storage',
        operation_description='Delete a specific S3 import storage connection.',
    ),
)
class S3ImportStorageDetailAPI(ImportStorageDetailAPI):
    queryset = S3ImportStorage.objects.all()
    serializer_class = S3ImportStorageSerializer

    def delete(self, request, *args, **kwargs):
        import_id = kwargs.get("pk")
        import_intance = S3ImportStorage.objects.filter(id=import_id).first()
        S3ExportStorage.objects.filter(id=import_intance.export_storage).delete()

        return super(S3ImportStorageDetailAPI, self).delete(request, *args, **kwargs)


@method_decorator(
    name='post',
    decorator=swagger_auto_schema(
        tags=['Storage:S3'],
        operation_summary='Sync import storage',
        operation_description='Sync tasks from an S3 import storage connection.',
    ),
)
class S3ImportStorageSyncAPI(ImportStorageSyncAPI):
    serializer_class = S3ImportStorageSerializer


@method_decorator(
    name='post',
    decorator=swagger_auto_schema(
        tags=['Storage:S3'],
        operation_summary='Validate import storage',
        operation_description='Validate a specific S3 import storage connection.',
    ),
)
class S3ImportStorageValidateAPI(ImportStorageValidateAPI):
    serializer_class = S3ImportStorageSerializer


@method_decorator(
    name='post',
    decorator=swagger_auto_schema(
        tags=['Storage:S3'],
        operation_summary='Validate export storage',
        operation_description='Validate a specific S3 export storage connection.',
    ),
)
class S3ExportStorageValidateAPI(ExportStorageValidateAPI):
    serializer_class = S3ExportStorageSerializer


@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=['Storage:S3'],
        operation_summary='Get all export storage',
        operation_description='Get a list of all S3 export storage connections.',
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
        tags=['Storage:S3'],
        operation_summary='Create export storage',
        operation_description='Create a new S3 export storage connection to store annotations.',
    ),
)
class S3ExportStorageListAPI(ExportStorageListAPI):
    queryset = S3ExportStorage.objects.all()
    serializer_class = S3ExportStorageSerializer


@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=['Storage:S3'],
        operation_summary='Get export storage',
        operation_description='Get a specific S3 export storage connection.',
    ),
)
@method_decorator(
    name='patch',
    decorator=swagger_auto_schema(
        tags=['Storage:S3'],
        operation_summary='Update export storage',
        operation_description='Update a specific S3 export storage connection.',
    ),
)
@method_decorator(
    name='delete',
    decorator=swagger_auto_schema(
        tags=['Storage:S3'],
        operation_summary='Delete export storage',
        operation_description='Delete a specific S3 export storage connection.',
    ),
)
class S3ExportStorageDetailAPI(ExportStorageDetailAPI):
    queryset = S3ExportStorage.objects.all()
    serializer_class = S3ExportStorageSerializer

    # def delete(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     auto_storage = S3ExportStorage.objects.filter(project_id = instance.project_id).first()
    #     if auto_storage.id == instance.id:
    #         return Response({"message": "S3 export storage connection cannot deleted."}, status=status.HTTP_204_NO_CONTENT)
    #     self.perform_destroy(instance)
    #     return Response({"message": "S3 export storage connection deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


@method_decorator(
    name='post',
    decorator=swagger_auto_schema(
        tags=['Storage:S3'],
        operation_summary='Sync export storage',
        operation_description='Sync tasks from an S3 export storage connection.',
    ),
)
class S3ExportStorageSyncAPI(ExportStorageSyncAPI):
    serializer_class = S3ExportStorageSerializer


class S3ImportStorageFormLayoutAPI(ImportStorageFormLayoutAPI):
    pass


class S3ExportStorageFormLayoutAPI(ExportStorageFormLayoutAPI):
    pass


@method_decorator(
    name='post',
    decorator=swagger_auto_schema(
        tags=['Storage:S3'],
        operation_summary='S3 Server Change Password',
        operation_description='S3 Server Change Password',
    ),
)
class S3ServerChangePassword(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        from django.conf import settings
        from minio import Minio

        user_email = request.user.email
        password_old = self.request.data.get('password_old')
        password_new = self.request.data.get('password_new')

        try:
            client_service = Minio(
                settings.MINIO_API_URL,
                access_key=user_email,
                secret_key=password_old,
                secure=False
            )

            client_service.list_buckets()

            s3_server = S3Server(user_email)
            password = s3_server.create_user(password_new)

            return Response({"message": password}, status=200)


        except:
            return Response({"message": "Password Incorrect!"}, status=401)



@method_decorator(
    name='post',
    decorator=swagger_auto_schema(
        tags=['Storage:S3'],
        operation_summary='S3 Server Change Password',
        operation_description='S3 Server Change Password',
    ),
)
class S3ServerResetPassword(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        user_email = request.user.email

        try:
            s3_server = S3Server()
            user_existed = s3_server.check_user(user_email)
            if not user_existed:
                return Response({"message": "User not exist!"}, status=400)

            password = s3_server.create_user()
            
            return Response({"message": password}, status=200)


        except:
            return Response({"message": "Password Incorrect!"}, status=401)
    