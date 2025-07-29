from minio import Minio

from core.settings.base import MINIO_API_URL


class MinioClient:
    """
    A class to interact with MinIO object storage server. Consider moving it to common place for 
    utilities/packages if needs to reuse
    """

    def __init__(self, endpoint=MINIO_API_URL, access_key="", secret_key=""):
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False  # remove this when server has HTTPS
        )

    def process_bucket_name(self, bucket_name):
        return bucket_name.replace('_', '-').replace(' ', '-')

    def create_bucket(self, bucket_name):
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)

    def put_object(self, bucket_name, object_name, file_path):
        bucket_name = self.process_bucket_name(bucket_name)
        self.create_bucket(bucket_name)
        self.client.fput_object(bucket_name, object_name, file_path)

    def get_object(self, bucket_name, object_name, save_path):
        bucket_name = self.process_bucket_name(bucket_name)
        self.client.fget_object(bucket_name, object_name, save_path)
    
    def get_objects(self, bucket_name, object_name, save_path):
        bucket_name = self.process_bucket_name(bucket_name)
        for item in self.client.list_objects(bucket_name, prefix=object_name, recursive=True):
            local_path = f'{save_path}/{item.object_name.replace(object_name, "")}'
            self.client.fget_object(bucket_name, item.object_name, local_path)

    def url_download_file(self, bucket_name, object_name):
        bucket_name = self.process_bucket_name(bucket_name)

        url = self.client.presigned_get_object(
            bucket_name=bucket_name,
            object_name=object_name
        )

        return url

    def get_list_project(self, bucket_name, object_name):
        bucket_name = self.process_bucket_name(bucket_name)
        folders = set()
        for item in self.client.list_objects(bucket_name, prefix=object_name, recursive=True):
            # Tách các phần của đường dẫn đối tượng
            parts = item.object_name.split('/')
            if len(parts) > 1:
                # Thêm tên thư mục vào set
                folders.add(parts[1])
                
        return list(folders)