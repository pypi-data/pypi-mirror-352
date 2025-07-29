"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import logging
import inspect
import os

from rest_framework import generics
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from drf_yasg import openapi as openapi
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema

from core.permissions import all_permissions
from core.utils.common import get_object_with_check_and_log
from core.utils.io import read_yaml
from io_storages.serializers import ImportStorageSerializer, ExportStorageSerializer
from projects.models import Project
from core.services.minio_client import MinioClient
from core.permissions import IsSuperAdminOrg

from organizations.models import OrganizationMember, Organization
from rest_framework.exceptions import ValidationError
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

from io_storages.s3.storage_server import S3Server

logger = logging.getLogger(__name__)


class ImportStorageListAPI(generics.ListCreateAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_required = all_permissions.projects_change
    serializer_class = ImportStorageSerializer

    def get_queryset(self):
        project_pk = self.request.query_params.get('project')
        project = get_object_with_check_and_log(self.request, Project, pk=project_pk)
        self.check_object_permissions(self.request, project)
        ImportStorageClass = self.serializer_class.Meta.model
        return ImportStorageClass.objects.filter(project=project)

    def post(self, request, *args, **kwargs):
        project = Project.objects.get(id=self.request.data.get('project'))
        check_org_admin = OrganizationMember.objects.filter(organization_id=project.organization_id,
                                                            user_id=self.request.user.id, is_admin=True).exists()
        
        if not check_org_admin and not self.request.user.is_superuser:
            raise ValidationError(
                "You do not have permission to setup this project", code=403
            )

        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        # Save the storage object
        storage = serializer.save()

        # Sync logic for another storage
        def sync_another_storage(storage):
            try:
                storage.create_folder(f"raw_files_{project.pk}")
                # from io_storages.s3.models import S3ImportStorage

                # if storage != S3ImportStorage.objects.filter(project_id=storage.project_id).first():
                #     s3_prj = S3ImportStorage.objects.filter(project_id=storage.project_id).first()
                #     storage.alias_storage(s3_prj)
                #     storage.copy_storage(s3_prj)
                    
            except Exception as e:
                print(e)

        import threading

        storage_thread = threading.Thread(target=sync_another_storage, args=(storage,))
        storage_thread.start()

        return Response(self.serializer_class(storage).data)
    # return super(ImportStorageListAPI, self).post(request, *args, **kwargs)

class ImportStorageDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    """RUD storage by pk specified in URL"""

    parser_classes = (JSONParser, FormParser, MultiPartParser)
    serializer_class = ImportStorageSerializer
    permission_required = all_permissions.projects_change
    permission_classes = [IsSuperAdminOrg]

    @swagger_auto_schema(auto_schema=None)
    def put(self, request, *args, **kwargs):
        return super(ImportStorageDetailAPI, self).put(request, *args, **kwargs)

    # def patch(self, request, *args, **kwargs):
    #     # try:
    #     project = Project.objects.get(id=self.request.data.get('project'))
    #     check_org_admin = OrganizationMember.objects.filter(organization_id = project.organization_id, user_id=self.request.user.id, is_admin=True).exists()
    #     if not check_org_admin:
    #         if not project.organization.created_by_id == self.request.user.id and not self.request.user.is_superuser:
    #             raise ValidationError("You do not have permission to setup this storage", code=403)
    #     # except Exception as e:
    #     #     print(e)
    #     return super(ImportStorageDetailAPI, self).patch(request, *args, **kwargs)
    
    # def delete(self, request, *args, **kwargs):
    #     project = Project.objects.get(id=self.request.data.get('project'))
    #     check_org_admin = OrganizationMember.objects.filter(organization_id = project.organization_id, user_id=self.request.user.id, is_admin=True).exists()
    #     if not check_org_admin:
    #         if not project.organization.created_by_id == self.request.user.id and not self.request.user.is_superuser:
    #             return Response({"message": "You do not have permission to delete this storage"}, status=403)
    #     return super(ImportStorageDetailAPI, self).delete(request, *args, **kwargs)

class ExportStorageListAPI(generics.ListCreateAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_required = all_permissions.projects_change
    serializer_class = ExportStorageSerializer

    def get_queryset(self):
        project_pk = self.request.query_params.get('project')
        project = get_object_with_check_and_log(self.request, Project, pk=project_pk)
        self.check_object_permissions(self.request, project)
        ImportStorageClass = self.serializer_class.Meta.model
        return ImportStorageClass.objects.filter(project_id=project.id)

    def perform_create(self, serializer):
        if self.request.data.get('is_global') == 1 or self.request.data.get('project') == None:
            print(self.request.data)
            # del self.request.data["null"]
            kwargs = self.request.data
            if kwargs.get('storage_type') == "s3":
 
                # export_storage = S3ExportStorage.objects.create(
                #     # project=kwargs.get('pk'),
                #     title=kwargs.get('title'),
                #     bucket=kwargs.get('path'),
                #     prefix=kwargs.get('prefix'),
                #     regex_filter=kwargs.get('regex'),
                #     use_blob_urls=True,
                #     region_name=kwargs.get('region_name'),
                # )
                
                storage = S3ImportStorage(title=kwargs.get('title'), region_name=kwargs.get('region_name'),bucket=kwargs.get('bucket'), 
                                                        aws_access_key_id = kwargs.get('aws_access_key_id'), 
                                                        aws_secret_access_key = kwargs.get('aws_secret_access_key'), 
                                                        s3_endpoint = kwargs.get('s3_endpoint').strip(), 
                                                        aws_session_token = kwargs.get('aws_session_token'), 
                                                        use_blob_urls=True, 
                                                        regex_filter=kwargs.get('regex_filter'),
                                                        is_global=True,
                                                        user_id=self.request.user.id,
                                                        project_id=kwargs.get('pk'),
                                                        org_id=self.request.user.active_organization_id)
                storage.validate_connection()
                storage.save()
                storage.refresh_from_db()
                return Response(status=200)
            elif kwargs.get('storage_type', "") == "azure":
                
                storage = AzureBlobImportStorage(
                    title=kwargs.get('title'),
                    # export_storage=export_storage.id,
                    # project=kwargs.get('pk'),
                    container=kwargs.get('container'),
                    prefix=kwargs.get('prefix'),
                    regex_filter=kwargs.get('regex_filter'),
                    account_name = kwargs.get('account_name'),
                    account_key = kwargs.get('account_key'),
                    use_blob_urls=True,
                    is_global=True,
                    user_id=self.request.user.id,org_id=self.request.user.active_organization_id,project_id=kwargs.get('pk')
                )
                storage.validate_connection()
                storage.save()
                storage.refresh_from_db()
                return Response(status=200)
            elif kwargs.get('storage_type', "") == "redis":
               
                storage = RedisImportStorage(
                    title=kwargs.get('title'),
                    # export_storage=export_storage.id,
                    # project=kwargs.get('pk'),
                    path=kwargs.get('path'),
                    host=kwargs.get('host'),
                    port=kwargs.get('port'),
                    password=kwargs.get('password'),is_global=True,user_id=self.request.user.id,org_id=self.request.user.active_organization_id,project_id=kwargs.get('pk')
                )
                storage.validate_connection()
                storage.save()
                storage.refresh_from_db()
                return Response(status=200)
            
            elif kwargs.get('storage_type', "") == "gdriver":
                
                storage = GDriverImportStorage(
                    title=kwargs.get('title'),
                    # export_storage=export_storage.id,
                    # project=kwargs.get('pk'),
                    bucket=kwargs.get('bucket'),
                    prefix=kwargs.get('prefix'),
                    regex_filter=kwargs.get('regex'),
                    google_application_credentials=kwargs.get('google_application_credentials'),
                    use_blob_urls=True,is_global=True,user_id=self.request.user.id,org_id=self.request.user.active_organization_id
                )
                storage.validate_connection()
                storage.save()
                storage.refresh_from_db()
                return Response(status=200)
            elif kwargs.get('storage_type', "") == "gcs":
               
                storage = GCSImportStorage(
                    title=kwargs.get('title'),
                    # export_storage=export_storage.id,
                    project=kwargs.get('pk'),
                    bucket=kwargs.get('bucket'),
                    prefix=kwargs.get('prefix'),
                    regex_filter=kwargs.get('regex_filter'),
                    google_application_credentials=kwargs.get('google_application_credentials'),
                    use_blob_urls=True,is_global=True,user_id=self.request.user.id,org_id=self.request.user.active_organization_id
                )
                storage.validate_connection()
                storage.save()
                storage.refresh_from_db()
                return Response(status=200)
           
        else:
            project = Project.objects.get(id=self.request.data.get('project'))
            check_org_admin = OrganizationMember.objects.filter(organization_id = project.organization_id, user_id=self.request.user.id, is_admin=True).exists()
            if not check_org_admin:
                if not project.organization.created_by_id == self.request.user.id and not self.request.user.is_superuser:
                    raise ValidationError("You do not have permission to setup this project", code=403)

            import_id = self.request.data.get("import_id")
            serializer = self.get_serializer(data=self.request.data)
            serializer.is_valid(raise_exception=True)
            
            # Lưu đối tượng và lấy dữ liệu đã lưu
            storage = serializer.save()

            if import_id:
                storage.create_connect_to_import_storage(import_id)

            if settings.SYNC_ON_TARGET_STORAGE_CREATION:
                storage.sync()


class ExportStorageDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    """RUD storage by pk specified in URL"""

    parser_classes = (JSONParser, FormParser, MultiPartParser)
    serializer_class = ExportStorageSerializer
    permission_required = all_permissions.projects_change
    permission_classes = [IsSuperAdminOrg]

    @swagger_auto_schema(auto_schema=None)
    def put(self, request, *args, **kwargs):
        return super(ExportStorageDetailAPI, self).put(request, *args, **kwargs)

    # def patch(self, request, *args, **kwargs):
    #     project = Project.objects.get(id=self.request.data.get('project'))
    #     check_org_admin = OrganizationMember.objects.filter(organization_id = project.organization_id, user_id=self.request.user.id, is_admin=True).exists()
    #     if not check_org_admin:
    #         if not project.organization.created_by_id == self.request.user.id and not self.request.user.is_superuser:
    #             raise ValidationError("You do not have permission to setup this storage", code=403)
    #     return super(ExportStorageDetailAPI, self).patch(request, *args, **kwargs)

    # def delete(self, request, *args, **kwargs):
    #     project = Project.objects.get(id=self.request.data.get('project'))
    #     check_org_admin = OrganizationMember.objects.filter(organization_id = project.organization_id, user_id=self.request.user.id, is_admin=True).exists()
    #     if not check_org_admin:
    #         if not project.organization.created_by_id == self.request.user.id and not self.request.user.is_superuser:
    #             return Response({"message": "You do not have permission to delete this storage"}, status=403)
    #     return super(ExportStorageDetailAPI, self).delete(request, *args, **kwargs)

class ImportStorageSyncAPI(generics.GenericAPIView):

    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_required = all_permissions.projects_change
    serializer_class = ImportStorageSerializer

    def get_queryset(self):
        ImportStorageClass = self.serializer_class.Meta.model
        return ImportStorageClass.objects.all()

    def post(self, request, *args, **kwargs):
        storage = self.get_object()

        # Get the first project (or handle multiple projects if needed)
        if request.data and len(request.data) > 0:
            if "regex_filter" in request.data:
                storage.regex_filter = request.data["regex_filter"]
            if "use_blob_urls" in request.data:
                storage.use_blob_urls = request.data["use_blob_urls"]
            if "presign_ttl" in request.data:
                storage.presign_ttl = request.data["presign_ttl"]
            storage.save()

            if (
                "type_import" in request.data
                and request.data["type_import"] == "dataset"
            ):
                try:
                    from io_storages.functions import get_all_project_storage_with_name
                    storages = get_all_project_storage_with_name(storage.project.id)
                    # cloud_client = MinioClient(
                    #     access_key=storage.project.s3_access_key,  # Use `project` here instead of `storage.project`
                    #     secret_key=storage.project.s3_secret_key,
                    # )

                    # objects = cloud_client.get_list_project(
                    #     bucket_name=f"project_{storage.project.id}", object_name="dataset/"
                    # )

                    # for object in objects:
                    #     from model_marketplace.models import DatasetModelMarketplace

                    #     user = request.user
                    #     if not DatasetModelMarketplace.objects.filter(
                    #         name=object
                    #     ).exists():
                    #         DatasetModelMarketplace.objects.create(
                    #             name=object,
                    #             owner_id=user.id,
                    #             author_id=user.id,
                    #             project_id=storage.project.id,  # Use the first project
                    #             catalog_id=storage.project.template.catalog_model_id,
                    #             model_id=0,
                    #             order=0,
                    #             config=0,
                    #             dataset_storage_id=storage.id,
                    #             version=object,
                    #         )
                except Exception as e:
                    print(e)

        # check connectivity & access, raise an exception if not satisfied
        storage.validate_connection()
        storage.sync()
        storage.sync_export_storage()
        storage.refresh_from_db()
        return Response(self.serializer_class(storage).data)


class ExportStorageSyncAPI(generics.GenericAPIView):

    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_required = all_permissions.projects_change
    serializer_class = ExportStorageSerializer

    def get_queryset(self):
        ExportStorageClass = self.serializer_class.Meta.model
        return ExportStorageClass.objects.all()

    def post(self, request, *args, **kwargs):
        storage = self.get_object()
        # check connectivity & access, raise an exception if not satisfied
        storage.validate_connection()
        storage.sync()
        storage.refresh_from_db()
        return Response(self.serializer_class(storage).data)


class StorageValidateAPI(generics.CreateAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_required = all_permissions.projects_change

    def create(self, request, *args, **kwargs):
        instance = None
        storage_id = request.data.get('id')
        if storage_id:
            instance = generics.get_object_or_404(self.serializer_class.Meta.model.objects.all(), pk=storage_id)
            if not instance.has_permission(request.user):
                raise PermissionDenied()
        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response()


class StorageFormLayoutAPI(generics.RetrieveAPIView):

    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_required = all_permissions.projects_change
    swagger_schema = None
    storage_type = None

    @swagger_auto_schema(auto_schema=None)
    def get(self, request, *args, **kwargs):
        project_id = request.query_params.get('project_id')
        
        form_layout_file = os.path.join(os.path.dirname(inspect.getfile(self.__class__)), 'form_layout.yml')

        if not os.path.exists(form_layout_file):
            raise NotFound(f'"form_layout.yml" is not found for {self.__class__.__name__}')

        form_layout = read_yaml(form_layout_file)

        try:
            project = Project.objects.filter(id=project_id).first()

            data_type =  project.data_types
            if 'image' in data_type:
                filter_s3 = f"raw_files_{project.pk}/.+\.(jpg|png|jpeg|gif|webp|svg)"
            elif 'audio' in data_type:
                filter_s3 = f"raw_files_{project.pk}/.+\.(mp3|ogg|wav|m4a|m4b|aiff|au|flac)"
            elif 'video' in data_type:
                filter_s3 = f"raw_files_{project.pk}/.+\.(mp4|h264|webm|webm)"
            else:
                filter_s3 = f"raw_files_{project.pk}/.+\.(txt|csv|json|tsv)"

            field = next(
                (field for section in form_layout.get('ImportStorage', []) 
                for field in section.get('fields', []) 
                if field and field.get('label') == 'File Filter Regex'),
                None
            )

            if field:
                field['value'] = filter_s3
                
        except Exception as e:
            print(e)

        form_layout = self.post_process_form(form_layout)
        return Response(form_layout[self.storage_type])

    def post_process_form(self, form_layout):
        return form_layout


class ImportStorageValidateAPI(StorageValidateAPI):
    serializer_class = ImportStorageSerializer


class ExportStorageValidateAPI(StorageValidateAPI):
    serializer_class = ExportStorageSerializer


class ImportStorageFormLayoutAPI(StorageFormLayoutAPI):
    storage_type = 'ImportStorage'


class ExportStorageFormLayoutAPI(StorageFormLayoutAPI):
    storage_type = 'ExportStorage'
