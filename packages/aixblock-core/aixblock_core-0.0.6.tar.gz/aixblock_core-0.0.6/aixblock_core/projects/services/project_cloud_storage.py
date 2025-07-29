import threading

from core.services.minio_client import MinioClient
from projects.models import Project
import concurrent.futures

class ProjectCloudStorage:
    def __init__(self, cloud_client = None, bucket_prefix: str = "", object_prefix: str = "") -> None:
        self.cloud_client = cloud_client
        self.bucket_prefix = bucket_prefix
        self.object_prefix = object_prefix

    def set_client(self, client):
        self.cloud_client = client

    def _upload_file(self, project: Project, bucket_name: str, object_name: str, file_path: str, s3=None):
        try:
            if not s3:
                from io_storages.s3.models import S3ImportStorage
                s3 = S3ImportStorage.objects.filter(project_id=project.id).first()  
                              
            cloud_client = MinioClient(
                endpoint=s3.s3_endpoint.replace("http://", ""),
                access_key=s3.aws_access_key_id,
                secret_key=s3.aws_secret_access_key
            )
            bucket_name = s3.bucket
            # s3.create_storage_link(key=self.object_prefix + object_name)
        except Exception as e:
            print(e)
            bucket_name = self.bucket_prefix + bucket_name
            cloud_client = MinioClient(
                access_key=project.s3_access_key,
                secret_key=project.s3_secret_key
            )
        
        if self.bucket_prefix:
            cloud_client.put_object(
                bucket_name=bucket_name,
                object_name=self.object_prefix + object_name,
                file_path=file_path
            )
        else:
            cloud_client.put_object(
                bucket_name=bucket_name,
                object_name=self.object_prefix + object_name,
                file_path=file_path
            )
    
    def _upload_data(self, bucket_name: str, object_name: str, file_data):
        pass

    def _download_file(self, project: Project, bucket_name: str, object_name: str, save_path: str):
        cloud_client = MinioClient(
            access_key=project.s3_access_key,
            secret_key=project.s3_secret_key
        )
        cloud_client.get_object(
            bucket_name=self.bucket_prefix + bucket_name,
            object_name=self.object_prefix + object_name,
            save_path=save_path
        )

    def _download_data(self, bucket_name: str, object_name: str):
        pass

    def upload_file(self, project, bucket_name, object_name, file_path, new_thread: bool = True, s3=None):
        if new_thread:
            t = threading.Thread(target=self._upload_file, args=(project, bucket_name, object_name, file_path, s3))
            t.start()
        else:
            self._upload_file(project, bucket_name, object_name, file_path, s3)

    def download_file(self, project, bucket_name: str, object_name: str, save_path: str):
        self._download_file(project, bucket_name, object_name, save_path)

    def _upload_directory(self, project: Project, bucket_name: str, directory_path: str):
        import os
        for root, dirs, files in os.walk(directory_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                object_name = os.path.relpath(file_path, directory_path)
                self._upload_file(project, bucket_name, object_name, file_path)

    def upload_directory(self, project, bucket_name, directory_path, new_thread: bool = True):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.submit(self._upload_directory, project, bucket_name, directory_path)

    def get_list_object(self, project: Project, bucket_name: str, object_name: str, save_path: str):
        cloud_client = MinioClient(
            access_key=project.s3_access_key,
            secret_key=project.s3_secret_key
        )

        cloud_client.get_objects(
            bucket_name=self.bucket_prefix + bucket_name,
            object_name=self.object_prefix + object_name,
            save_path = save_path
        )
    
    def get_url_download_file(self, project: Project, bucket_name: str, object_name: str):
        cloud_client = MinioClient(
            access_key=project.s3_access_key,
            secret_key=project.s3_secret_key
        )
         
        url = cloud_client.url_download_file(
            bucket_name=self.bucket_prefix + bucket_name,
            object_name=self.object_prefix + object_name
        )

        return url

dataset_minio = ProjectCloudStorage(bucket_prefix="project-", object_prefix="dataset/")
checkpoint_minio = ProjectCloudStorage(bucket_prefix="project-", object_prefix="checkpoint/")
project_minio = ProjectCloudStorage(bucket_prefix="project-", object_prefix="raw_files/")
project_logs_minio = ProjectCloudStorage(bucket_prefix="project-", object_prefix="logs/")
project_minio_no_prefix = ProjectCloudStorage(bucket_prefix="", object_prefix="raw_files/")
