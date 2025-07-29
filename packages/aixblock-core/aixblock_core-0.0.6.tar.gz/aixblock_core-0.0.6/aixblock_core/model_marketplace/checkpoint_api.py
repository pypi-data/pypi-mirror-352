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
from .serializers import ModelCheckpointUploadSerializer
from projects.services.project_cloud_storage import checkpoint_minio

from rest_framework import generics, status
import os
import shutil
import zipfile
import datetime
import tempfile
from git import Repo
from roboflow import Roboflow
from datasets import load_dataset
from projects.services.project_cloud_storage import ProjectCloudStorage
from .models import CheckpointModelMarketplace
from .functions import build_jenkin_from_zipfle
from io_storages.functions import get_all_project_storage_with_name, get_storage_by_name

@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Checkpoint Model Marketplace'],
    operation_summary='Upload model checkpoint',
    operation_description='Upload model checkpoint',
    request_body=ModelCheckpointUploadSerializer
))
class ModelCheckpointUploadAPIView(APIView):
    parser_classes = (MultiPartParser, FileUploadParser)
    permission_required = ViewClassPermission(
        POST=all_permissions.annotations_view,
    )
    def post(self, request, checkpoint_id, *args, **kwargs):
        serializer = ModelCheckpointUploadSerializer(data=request.data)
        if serializer.is_valid():
            project = Project.objects.get(id=serializer.validated_data['project_id'])
            # TODO: Should not save file to disk => check file type and convert to byte and use minio client put_object
            temp_file_path = "minio_upload_temp"
            with open(temp_file_path, 'wb+') as temp_file:
                for chunk in serializer.validated_data['file'].chunks():
                    temp_file.write(chunk)

            checkpoint_minio.upload_file(
                project=project,
                bucket_name=str(project.id),
                object_name=str(checkpoint_id),
                file_path=temp_file_path,
                new_thread=False
            )
            os.remove(temp_file_path)
            return Response({'message': 'Model checkpoint uploaded successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Checkpoint Model Marketplace'],
    operation_summary='Download model checkpoint',
    operation_description='Download model checkpoint',
    manual_parameters=[
        openapi.Parameter(
            name='project_id',
            type=openapi.TYPE_INTEGER,
            in_=openapi.IN_QUERY,
            description='Project ID'
        ),
    ]))
class ModelCheckpointDownloadAPIView(APIView):
    permission_required = ViewClassPermission(
        POST=all_permissions.annotations_view,
    )
    def get(self, request, checkpoint_id, *args, **kwargs):
        project = Project.objects.get(id=self.request.query_params['project_id'])
        checkpoint_instance = CheckpointModelMarketplace.objects.filter(id=checkpoint_id).first()

        storage_id = checkpoint_instance.checkpoint_storage_id
        storage_name = checkpoint_instance.checkpoint_storage_name
        storage = get_storage_by_name(storage_name)
        storage_instance = storage['import_instance'].objects.filter(id=storage_id).first()

        checkpoint_path = f"checkpoint_{project.id}/{checkpoint_instance.version}"

        temp_zip_file = tempfile.NamedTemporaryFile()
        save_path = f"temporary-files-{checkpoint_instance.version}"
        os.makedirs(save_path, exist_ok=True)

        if checkpoint_instance.type == "GIT":
            # Clone repository từ GitHub
            repo_url = checkpoint_instance.version
            if checkpoint_instance.config and checkpoint_instance.config != "":
                repo_url = repo_url.replace("https://", f"https://{checkpoint_instance.config}@")
                
            Repo.clone_from(repo_url, save_path)

        elif checkpoint_instance.type == "HUGGING_FACE":
            repo_url = checkpoint_instance.version
            if "http" not in repo_url:
                repo_url = "https://huggingface.co/" + repo_url
            if checkpoint_instance.config and checkpoint_instance.config != "":
                repo_url = repo_url.replace("https://", f"https://{checkpoint_instance.config}@")
                
            Repo.clone_from(repo_url, save_path)
        else:
            storage_instance.download_and_save_folder(checkpoint_path, save_path)
            # with tempfile.TemporaryDirectory() as temp_dir:
            # checkpoint_minio.get_list_object(
            #     project=project,
            #     bucket_name=str(project.id),
            #     object_name=f"{checkpoint_instance.version}",
            #     save_path=f"temporary-files"
            # )

        with zipfile.ZipFile(temp_zip_file.name, 'w') as zipf:
            for root, dirs, files in os.walk(save_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, save_path))
            
        # response = FileResponse(open(temp_zip_file, "rb"), filename=str(checkpoint_id))
        response = FileResponse(open(temp_zip_file.name, "rb"), filename=str(checkpoint_id))
        response['Content-Disposition'] = f'attachment; filename="{checkpoint_id}.zip"'
        response['filename'] = f"{checkpoint_instance.version}.zip"
        response['X-Checkpoint-Name'] = checkpoint_instance.name
        shutil.rmtree(save_path)
        return response

@method_decorator(name='post', decorator=swagger_auto_schema(
        tags=['Import'],
        operation_summary='Upload checkpoint',
        operation_description='Upload checkpoint',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'type_checkpoint': openapi.Schema(type=openapi.TYPE_STRING, description='type_point'),
                'checkpoint_path':openapi.Schema(type=openapi.TYPE_STRING, description='checkpoint_path'),
                'checkpoint_name':openapi.Schema(type=openapi.TYPE_STRING, description='checkpoint_name'),
                'username':openapi.Schema(type=openapi.TYPE_STRING, description='username'),
                'token':openapi.Schema(type=openapi.TYPE_STRING, description='token'),
                'url':openapi.Schema(type=openapi.TYPE_STRING, description='url'),
                'version':openapi.Schema(type=openapi.TYPE_STRING, description='version'),
                'workspace':openapi.Schema(type=openapi.TYPE_STRING, description='workspace'),
                'project_id':openapi.Schema(type=openapi.TYPE_STRING, description='project_id'),
                'file': openapi.Schema(type=openapi.TYPE_FILE, description='checkpoint file')
            },
            required=['type_checkpoint', 'project_id']
        )
    ))
    
class ModelCheckpointUploadv2APIView(generics.ListAPIView):
    def post(self, request, *args, **kwargs):
        # user_id = self.request.query_params.get('user_id')
        type_checkpoint = self.request.data.get("type_checkpoint")
        username = self.request.data.get("username")
        checkpoint_path = self.request.data.get("checkpoint_path")
        checkpoint_name = self.request.data.get("checkpoint_name")
        token = self.request.data.get("token")
        url = self.request.data.get("url")
        version = self.request.data.get("version")
        workspace = self.request.data.get("workspace")
        project_id = self.request.data.get("project_id")
        file =  self.request.FILES.get("file")
        is_training = self.request.data.get("is_training")
        full_path = self.request.data.get("full_path", None)

        user = self.request.user
        project = Project.objects.filter(id=project_id).first()
        
        now = datetime.datetime.now()
        date_str = now.strftime("%Y%m%d")
        time_str = now.strftime("%H%M%S")
        
        valid_checkpoint = True
        
        if not version:
            version = f'{date_str}-{time_str}'

        if not full_path:
            dir_path = f"checkpoint_{project_id}/{version}"
        else:
            dir_path = f"checkpoint_{project_id}/{version}/{full_path}"
            version = full_path

        checkpoint_upload = ProjectCloudStorage(bucket_prefix="project-", object_prefix=dir_path)
        storages = get_all_project_storage_with_name(project.pk)

        success_upload = []

        def find_file_in_directory(start_dir, target_file):
            for root, dirs, files in os.walk(start_dir):
                if target_file in files:
                    return root
            return None

        try:
            if type_checkpoint == "kaggle":
                os.environ['KAGGLE_USERNAME'] = username
                os.environ['KAGGLE_KEY'] = token
                # os.environ['KAGGLE_USERNAME'] = 'phtrnquang'
                # os.environ['KAGGLE_KEY'] = 'de8911bf45f679a755b1e40005302d96'
                import kagglehub
                # path = kagglehub.model_download("tensorflow/resnet-50/tensorFlow2/classification")           
                path = kagglehub.model_download(checkpoint_path)           
                checkpoint_upload.upload_directory(
                    project=project,
                    bucket_name=str(project.id),
                    directory_path=path,
                    new_thread=True
                )
                if os.path.exists(path):
                    shutil.rmtree(path)

            elif type_checkpoint == "hugging-face":
                from huggingface_hub import hf_hub_download
                with tempfile.TemporaryDirectory() as temp_dir:
                    # dataset.save_to_disk(temp_dir)
                    # hf_hub_download(repo_id="tals/albert-xlarge-vitaminc-mnli", filename="model.safetensors", cache_dir=temp_dir, resume_download=True)
                    if token:
                        hf_hub_download(repo_id=checkpoint_path, filename=checkpoint_name, cache_dir=temp_dir, resume_download=True, token=token)
                    else:
                        hf_hub_download(repo_id=checkpoint_path, filename=checkpoint_name, cache_dir=temp_dir, resume_download=True)
                    folder_path = find_file_in_directory(temp_dir, checkpoint_name)
                    checkpoint_upload.upload_directory(
                        project=project,
                        bucket_name=str(project.id),
                        directory_path=folder_path,
                        new_thread=True
                    )

            elif type_checkpoint == "roboflow":
                # rf = Roboflow(api_key="pqJPoQ0D9BaIaW9gq026")
                rf = Roboflow(api_key=token)
                # project_rf = rf.workspace("sham-vg4tg").project("face-coverd-or-not")
                project_rf = rf.workspace(workspace).project(checkpoint_path)
                version_rf = 1
                if version:
                    version_rf = version
                version = project_rf.version(version_rf)
                model = version.model
                with tempfile.TemporaryDirectory() as temp_dir:
                    model.download(location=temp_dir)
                    # dataset = version.download("coco", location=temp_dir, overwrite=True)
                    checkpoint_upload.upload_directory(
                        project=project,
                        bucket_name=str(project.id),
                        directory_path=temp_dir,
                        new_thread=True
                    )
            
            elif type_checkpoint == "ml_checkpoint":
                LIST_CHECKPOINT_FORMAT = ['.pt', '.pth', '.bin', '.mar', '.pte', '.pt2', '.ptl', '.safetensors', '.onnx', '.keras', '.pb', '.ckpt', '.tflite', '.tfrecords', '.npy',
                                  '.npz', '.gguf', '.ggml', '.ggmf', '.ggjt', '.nc', '.mleap', '.coreml', '.surml', '.llamafile', '.prompt', '.pkl', '.h5', '.caffemodel', 
                                  '.prototxt', '.dlc']
                file_name = os.path.splitext(file.name)[-1].lower()
                def check_files_in_zip(file):
                    try:
                        with zipfile.ZipFile(file, 'r') as zip_ref:
                            zip_file_list = zip_ref.namelist()
                            for zip_file in zip_file_list:
                                ext = os.path.splitext(zip_file)[-1].lower()
                                if ext in LIST_CHECKPOINT_FORMAT:
                                    return True
                            return False
                    except zipfile.BadZipFile:
                        return False
                    
                if file_name in ['.zip', '.rar', '.gz', '.tar.gz']:
                    valid_checkpoint = check_files_in_zip(file)
                # else:
                #     valid_checkpoint = os.path.splitext(file.name)[-1].lower() in LIST_CHECKPOINT_FORMAT
                
                if not valid_checkpoint:
                    return Response({"error": "There is no valid checkpoint available."}, status=400)
                

                with tempfile.TemporaryDirectory() as temp_dir:
                    # Save the uploaded file in the temporary directory
                    file_path = os.path.join(temp_dir, file.name)

                    with open(file_path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)

                    for storage in storages:
                        try:
                            storage.upload_directory(temp_dir, dir_path)
                            success_upload.append(storage)
                        except Exception as e:
                            print(e)

                    # checkpoint_upload.upload_directory(
                    #         project=project,
                    #         bucket_name=str(project.id),
                    #         directory_path=temp_dir,
                    #         new_thread=True
                    #     )   
                              
            else:
                # token = "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"
                # git_url = "https://github.com/phutqwow/coco_dataset.git"  # Thay bằng URL GitHub thực tế
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Clone repository từ GitHub
                    repo_url = url
                    if token:
                        repo_url = url.replace("https://", f"https://{token}@")
                    Repo.clone_from(repo_url, temp_dir)
                    folder_path = find_file_in_directory(temp_dir, checkpoint_name)
                    
                    # Repo.clone_from(repo_url, temp_dir)
                    checkpoint_upload.upload_directory(
                        project=project,
                        bucket_name=str(project.id),
                        directory_path=folder_path,
                        new_thread=True
                    )

            user = self.request.user
            from ml.models import MLBackend, MLBackendStatus
            ml_backend = MLBackend.objects.filter(project_id=project.id, deleted_at__isnull=True).first()
            MLBackendStatus.objects.filter(project_id=project.id, deleted_at__isnull=True, status="master").update(status="worker", status_training="reject_master")
            if ml_backend:
                ml_id=ml_backend.id
            else:
                ml_id=0

            for storage in success_upload:
                if CheckpointModelMarketplace.objects.filter(version=version).exists():
                    checkpoint_instance = CheckpointModelMarketplace.objects.filter(version=version).update(file_name=checkpoint_name, owner_id=user.id, author_id=user.id, project_id=project.id, ml_id=ml_id,
                                                    catalog_id=project.template.catalog_model_id, model_id=0, order=0, config=0, checkpoint_storage_id=storage.id, checkpoint_storage_name=storage.storage_name, version=version)
                    checkpoint_instance = CheckpointModelMarketplace.objects.filter(version=version).first()
                else:
                    checkpoint_instance = CheckpointModelMarketplace.objects.create(name=version, file_name=checkpoint_name, owner_id=user.id, author_id=user.id, project_id=project.id, ml_id=ml_id,
                                                    catalog_id=project.template.catalog_model_id, model_id=0, order=0, config=0, checkpoint_storage_id=storage.id, checkpoint_storage_name=storage.storage_name, version=version)

            if is_training and is_training == "True":
                html_file_path =  './templates/mail/training_completed.html'
                with open(html_file_path, 'r', encoding='utf-8') as file:
                    html_content = file.read()
                
                import threading
                from aixblock_core.users.service_notify import send_email_thread
                from core.settings.base import MAIL_SERVER


                html_content = html_content.replace('[user]', f'{user.email}')

                data = {
                    "subject": "Your AI Model Training is Complete!",
                    "from": "noreply@aixblock.io",
                    "to": [f'{user.email}'],
                    "html": html_content,
                    "text": "Welcome to AIxBlock!",
                    "attachments": []
                }

                docket_api = "tcp://69.197.168.145:4243"
                host_name = MAIL_SERVER

                email_thread = threading.Thread(target=send_email_thread, args=(docket_api, host_name, data,))
                email_thread.start() 

            response = Response("success")
            response['X-Checkpoint-Name'] = checkpoint_instance.name

            return response
        
        except Exception as e:
            return Response({"error": str(e)}, status=400)
        
@method_decorator(name='post', decorator=swagger_auto_schema(
        tags=['Import'],
        operation_summary='Upload Model Source',
        operation_description='Upload Model Source',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'type_checkpoint': openapi.Schema(type=openapi.TYPE_STRING, description='type_point'),
                'checkpoint_path':openapi.Schema(type=openapi.TYPE_STRING, description='checkpoint_path'),
                'checkpoint_name':openapi.Schema(type=openapi.TYPE_STRING, description='checkpoint_name'),
                'username':openapi.Schema(type=openapi.TYPE_STRING, description='username'),
                'token':openapi.Schema(type=openapi.TYPE_STRING, description='token'),
                'url':openapi.Schema(type=openapi.TYPE_STRING, description='url'),
                'version':openapi.Schema(type=openapi.TYPE_STRING, description='version'),
                'workspace':openapi.Schema(type=openapi.TYPE_STRING, description='workspace'),
                'name_model_source':openapi.Schema(type=openapi.TYPE_STRING, description='name_model_source'),
                'project_id':openapi.Schema(type=openapi.TYPE_STRING, description='project_id')
            },
            required=['type_checkpoint', 'project_id']
        )
    ))
    
class UploadModelSourceAPI(generics.ListAPIView):
    def post(self, request, *args, **kwargs):
        # user_id = self.request.query_params.get('user_id')
        type_checkpoint = self.request.data.get("type_checkpoint")
        username = self.request.data.get("username")
        checkpoint_path = self.request.data.get("checkpoint_path")
        checkpoint_name = self.request.data.get("checkpoint_name")
        token = self.request.data.get("token")
        url = self.request.data.get("url")
        version = self.request.data.get("version")
        workspace = self.request.data.get("workspace")
        name_model_source = self.request.data.get("name_model_source")
        project_id = self.request.data.get("project_id")

        project = Project.objects.filter(id=project_id).first()
        
        now = datetime.datetime.now()
        date_str = now.strftime("%Y%m%d")
        time_str = now.strftime("%H%M%S")
        
        # version = f'{date_str}-{time_str}'
        dir_path = f"name_model_source/"
        model_upload = ProjectCloudStorage(bucket_prefix="project-", object_prefix=dir_path)

        uploaded_file = request.FILES['file']

        try:
            if uploaded_file:
                image_build = build_jenkin_from_zipfle(uploaded_file, None)
                if image_build:
                    return Response({"message": "File uploaded and processed successfully", "images": image_build}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "File uploaded and processed failed", "images": None}, status=status.HTTP_400_BAD_REQUEST)

            if type_checkpoint == "hugging-face":
                from huggingface_hub import snapshot_download
                with tempfile.TemporaryDirectory() as temp_dir:
                    # dataset.save_to_disk(temp_dir)
                    # hf_hub_download(repo_id="tals/albert-xlarge-vitaminc-mnli", filename="model.safetensors", cache_dir=temp_dir, resume_download=True)
                    if token:
                        snapshot_download(repo_id=url, cache_dir=temp_dir, resume_download=True, token=token)
                    else:
                        snapshot_download(repo_id=url, cache_dir=temp_dir, resume_download=True)

                    model_upload.upload_directory(
                        project=project,
                        bucket_name=str(project.id),
                        directory_path=temp_dir,
                        new_thread=True
                    )

            # elif type_checkpoint == "roboflow":
            #     # rf = Roboflow(api_key="pqJPoQ0D9BaIaW9gq026")
            #     rf = Roboflow(api_key=token)
            #     # project_rf = rf.workspace("sham-vg4tg").project("face-coverd-or-not")
            #     project_rf = rf.workspace(workspace).project(checkpoint_path)
            #     version_rf = 1
            #     if version:
            #         version_rf = version
            #     version = project_rf.version(version_rf)
            #     model = version.model
            #     with tempfile.TemporaryDirectory() as temp_dir:
            #         model.download(location=temp_dir)
            #         # dataset = version.download("coco", location=temp_dir, overwrite=True)
            #         checkpoint_upload.upload_directory(
            #             project=project,
            #             bucket_name=str(project.id),
            #             directory_path=temp_dir,
            #             new_thread=True
            #         )
            
            else:
                # token = "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"
                # git_url = "https://github.com/phutqwow/coco_dataset.git"  # Thay bằng URL GitHub thực tế
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Clone repository từ GitHub
                    repo_url = url
                    if token:
                        repo_url = url.replace("https://", f"https://{token}@")
                        
                    Repo.clone_from(repo_url, temp_dir)
                    # folder_path = find_file_in_directory(temp_dir, checkpoint_name)
                    
                    # Repo.clone_from(repo_url, temp_dir)
                    model_upload.upload_directory(
                        project=project,
                        bucket_name=str(project.id),
                        directory_path=temp_dir,
                        new_thread=True
                    )

            # user = self.request.user
            # from ml.models import MLBackend
            # ml_backend = MLBackend.objects.filter(project_id=project.id).first()

            # if ml_backend:
            #     ml_id=ml_backend.id
            # else:
            #     ml_id=0

            # CheckpointModelMarketplace.objects.create(name=version, owner_id=user.id, author_id=user.id, project_id=project.id, ml_id=ml_id,
            #                                        catalog_id=project.template.catalog_model_id, model_id=0, order=0, config=0, checkpoint_storage_id=0, version=version)

            return Response("success")
        
        except Exception as e:
            return Response({"error": str(e)}, status=400)