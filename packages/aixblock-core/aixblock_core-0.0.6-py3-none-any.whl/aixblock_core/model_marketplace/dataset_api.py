import os
from django.http import FileResponse
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FileUploadParser
from drf_yasg.utils import swagger_auto_schema
import drf_yasg.openapi as openapi

from core.permissions import ViewClassPermission, all_permissions
from projects.models import Project
from .serializers import ModelDatasetUploadSerializer
from projects.services.project_cloud_storage import dataset_minio

from .models import DatasetModelMarketplace
from rest_framework import generics, status
import os
import shutil
import zipfile
import datetime
import tempfile
from git import Repo
from roboflow import Roboflow
from projects.services.project_cloud_storage import ProjectCloudStorage
from io_storages.functions import get_all_project_storage_with_name, get_storage_by_name

@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Dataset Model Marketplace'],
    operation_summary='Upload model dataset',
    operation_description='Upload model dataset',
    request_body=ModelDatasetUploadSerializer
))
class ModelDatasetUploadAPIView(APIView):
    parser_classes = (MultiPartParser, FileUploadParser)
    permission_required = ViewClassPermission(
        POST=all_permissions.annotations_view,
    )
    def post(self, request, dataset_id, *args, **kwargs):
        serializer = ModelDatasetUploadSerializer(data=request.data)
        if serializer.is_valid():
            project = Project.objects.get(id=serializer.validated_data['project_id'])
            # TODO: Should not save file to disk => check file type and convert to byte and use minio client put_object
            temp_file_path = "minio_upload_temp"
            with open(temp_file_path, 'wb+') as temp_file:
                for chunk in serializer.validated_data['file'].chunks():
                    temp_file.write(chunk)
            dataset_minio.upload_file(
                project=project,
                bucket_name=str(project.id),
                object_name=str(dataset_id),
                file_path=temp_file_path,
                new_thread=False
            )
            os.remove(temp_file_path)
            return Response({'message': 'Model dataset uploaded successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Dataset Model Marketplace'],
    operation_summary='Download model dataset',
    operation_description='Download model dataset',
    manual_parameters=[
        openapi.Parameter(
            name='project_id',
            type=openapi.TYPE_INTEGER,
            in_=openapi.IN_QUERY,
            description='Project ID'
        ),
    ]))
class ModelDatasetDownloadAPIView(APIView):
    permission_required = ViewClassPermission(
        POST=all_permissions.annotations_view,
    )
    def get(self, request, dataset_id, *args, **kwargs):
        project = Project.objects.get(id=self.request.query_params['project_id'])
        dataset_instance = DatasetModelMarketplace.objects.filter(id=dataset_id).first()
        temp_zip_file = tempfile.NamedTemporaryFile(delete=False)

        storage_id = dataset_instance.dataset_storage_id
        storage_name = dataset_instance.dataset_storage_name
        storage = get_storage_by_name(storage_name)
        storage_instance = storage['import_instance'].objects.filter(id=storage_id).first()

        save_path = f"temporary-files-{dataset_instance.version}"
        os.makedirs(save_path, exist_ok=True)

        dataset_path = f"dataset_{project.id}/{dataset_instance.version}"
        storage_instance.download_and_save_folder(dataset_path, save_path, all_path=False)
        # with tempfile.TemporaryDirectory() as temp_dir:
        # dataset_minio.get_list_object(
        #     project=project,
        #     bucket_name=str(project.id),
        #     object_name=f"{dataset_instance.version}",
        #     save_path=f"temporary-files"
        # )

        with zipfile.ZipFile(temp_zip_file.name, 'w') as zipf:
            for root, dirs, files in os.walk(save_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, save_path))
            
        # response = FileResponse(open(temp_zip_file, "rb"), filename=str(checkpoint_id))
        response = FileResponse(open(temp_zip_file.name, "rb"), filename=str(dataset_id))
        response['Content-Disposition'] = f'attachment; filename="{dataset_id}.zip"'
        response['filename'] = f"{dataset_instance.version}.zip"
        response['X-Dataset-Name'] = dataset_instance.name
        shutil.rmtree(save_path)
        # if os.path.exists(temp_zip_file.name):
        #     os.unlink(temp_zip_file.name)
        return response
