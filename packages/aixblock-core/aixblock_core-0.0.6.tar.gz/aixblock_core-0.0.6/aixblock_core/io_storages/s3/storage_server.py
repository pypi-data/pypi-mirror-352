from minio.credentials import StaticProvider
from datetime import timedelta
from urllib3 import PoolManager
import certifi
import os
import json
import re
import secrets
import string
import random

from minio import Minio, MinioAdmin

from django.conf import settings

# Cấu hình MinIO Admin
MINIO_HOST = settings.MINIO_API_URL
ADMIN_ACCESS_KEY = settings.MINIO_USER
ADMIN_SECRET_KEY = settings.MINIO_PASSWORD


def email_to_bucket_name(email):
    """Chuyển đổi email thành tên bucket hợp lệ theo chuẩn MinIO."""
    email = email.lower()  # Chuyển thành chữ thường
    email = email.replace('@', '-')  # Thay @ bằng dấu '-'
    email = re.sub(r'[^a-z0-9.-]', '-', email)  # Thay ký tự không hợp lệ bằng '-'
    email = email.strip('-')  # Xóa dấu '-' ở đầu/cuối
    return email[:63]  # Giới hạn tối đa 63 ký tự

def generate_password(length=12):
    """Tạo mật khẩu ngẫu nhiên với độ dài cố định"""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choices(characters, k=length))

class S3Server:
    def __init__(self, username, bucket_name=None) -> None:
        self.endpoint = f"http://{MINIO_HOST}"
        self.credentials  = StaticProvider(ADMIN_ACCESS_KEY, ADMIN_SECRET_KEY)

        self.admin_client = MinioAdmin(
            endpoint=MINIO_HOST,
            credentials=self.credentials,
            secure=False,  # Nếu dùng HTTP thì phải đặt `secure=False`
            cert_check=False,  
            http_client=PoolManager(
                timeout=timedelta(minutes=5).seconds,
                maxsize=10,
                cert_reqs='CERT_NONE',
                ca_certs=os.environ.get('SSL_CERT_FILE') or certifi.where(),
            )
        )

        self.client_service = Minio(
            MINIO_HOST,
            access_key=ADMIN_ACCESS_KEY,
            secret_key=ADMIN_SECRET_KEY,
            secure=False  # False nếu MinIO không dùng HTTPS
        )

        self.username = username
        if not bucket_name:
            self.bucket_name = email_to_bucket_name(self.username)
        else:
            self.bucket_name = bucket_name
    
    def create_bucket(self):
        print("Bucket Name:", self.bucket_name)

        if not self.client_service.bucket_exists(self.bucket_name):
            self.client_service.make_bucket(self.bucket_name)
            self.admin_client.bucket_quota_set(self.bucket_name, 2*1073741824)
            print(f"Bucket '{self.bucket_name}' created successfully!")
        else:
            print(f"Bucket '{self.bucket_name}' already exists!")
        
        
        return self.bucket_name
    
    def create_policy(self):
        # Định nghĩa policy JSON
        policy_name = f"{self.username}-policy"

        policy_json = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
                    "Resource": [f"arn:aws:s3:::{self.bucket_name}/*"]
                },
                {
                    "Effect": "Allow",
                    "Action": ["s3:ListBucket"],
                    "Resource": [f"arn:aws:s3:::{self.bucket_name}"]
                }
            ]
        }

        # **Lưu policy vào file**
        policy_file_path = f"/tmp/{policy_name}.json"
        with open(policy_file_path, "w", encoding="utf-8") as file:
            json.dump(policy_json, file)

        policy_data = json.loads(self.admin_client.policy_list())
        policy_list = list(policy_data.keys())

        if policy_name not in policy_list:
            # **Tạo policy trong MinIO**
            self.admin_client.policy_add(policy_name, policy_file_path)
            print(f"Policy '{policy_name}' created successfully.")        
        else:
            print(f"Policy '{policy_name}' already exists!")

        # **Gán policy cho user**
        self.admin_client.policy_set(policy_name=policy_name, user=self.username)
        print(f"Policy '{policy_name}' assigned to user '{self.username}'.")

        return policy_name, policy_file_path
    
    def create_user(self, password=None):
        user_data = json.loads(self.admin_client.user_list())
        # Lấy danh sách tên user
        user_list = list(user_data.keys())
        if self.username in user_list:
            print(f"User '{self.username}' already exists!")
            return None
        
        if not password:
            password = generate_password()

        self.admin_client.user_add(self.username, password)
        print(f"User '{self.username}' created successfully.")

        return password
    
    def check_user(self):
        user_data = json.loads(self.admin_client.user_list())
        # Lấy danh sách tên user
        user_list = list(user_data.keys())
        if self.username in user_list:
            print(f"User '{self.username}' already exists!")
            return True
        else:
            return False

    def create_service(self):
        self.create_bucket()
        password = self.create_user()
        # service_account = self.admin_client.list_service_account(self.username)
        # print(service_account)

        policy_name, policy_file_path = self.create_policy()

        # **Gán policy cho user**
        self.admin_client.policy_set(policy_name=policy_name, user=self.username)
        print(f"Policy '{policy_name}' assigned to user '{self.username}'.")

        policy_description = f"Service account for {self.username}"

        response = self.admin_client.add_service_account(
            # access_key=service_access_key,
            # secret_key=service_secret_key,
            name=policy_name,
            description=policy_description,
            policy_file=policy_file_path
        )

        os.remove(policy_file_path)
        
        print(f"Service Account created: {response}")
        response_dict = json.loads(response)

        accessKey, secretKey = response_dict["credentials"]["accessKey"], response_dict["credentials"]["secretKey"]

        result = {
            "endpoint": self.endpoint,
            "host_address": settings.MINIO_API_IP,
            "bucketname": self.bucket_name,
            "username": self.username,
            "password": password,
            "accessKey": accessKey,
            "secretKey": secretKey
        }
        return result