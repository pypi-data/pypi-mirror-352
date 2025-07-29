import typing
import json
from minio import MinioAdmin
from minio.credentials import StaticProvider

from core.settings.base import MINIO_API_URL, MINIO_USER, MINIO_PASSWORD


class MinioAdminService:
    """
    A class to work with admin functionalities in MinIO server
    """

    def __init__(self, endpoint, username, password):
        self.credentials = StaticProvider(
            access_key=username,
            secret_key=password
        )

        self.admin = MinioAdmin(
            endpoint=endpoint,
            credentials=self.credentials,
            secure=False  # remove this when server has HTTPS
        )

    def add_user(self, username, password):
        r = self.admin.user_add(
            access_key=username,
            secret_key=password
        )

    def add_access_key(self, access_key: str = None, secret_key: str = None) -> typing.Tuple[str]:
        try:
            res = self.admin.add_service_account(access_key, secret_key)
            res = json.loads(res)
            cred = res.get("credentials")
            access_key = cred.get("accessKey")
            secret_key = cred.get("secretKey")
        except:
            access_key = secret_key = ""
        return access_key, secret_key
    
    def delete_access_key(self):
        pass
   

minio_admin = MinioAdminService(
    endpoint=MINIO_API_URL,
    username=MINIO_USER,
    password=MINIO_PASSWORD
)
