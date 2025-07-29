from .s3.api import S3ImportStorageListAPI, S3ExportStorageListAPI
from .gcs.api import GCSImportStorageListAPI, GCSExportStorageListAPI
from .azure_blob.api import AzureBlobImportStorageListAPI, AzureBlobExportStorageListAPI
from .redis.api import RedisImportStorageListAPI, RedisExportStorageListAPI
from .gdriver.api import GDriverImportStorageListAPI,  GDriverExportStorageListAPI

from .s3.models import S3ImportStorage, S3ExportStorage
from .gcs.models import GCSImportStorage, GCSExportStorage
from .azure_blob.models import AzureBlobImportStorage, AzureBlobExportStorage
from .redis.models import RedisImportStorage, RedisExportStorage
from .gdriver.models import GDriverImportStorage, GDriverExportStorage

def get_storage_list():
    return [
        {'name': 's3', 'title': 'AWS S3', 'import_list_api': S3ImportStorageListAPI, 'export_list_api': S3ExportStorageListAPI},
        {'name': 'gcs', 'title': 'Google Cloud Storage', 'import_list_api': GCSImportStorageListAPI, 'export_list_api': GCSExportStorageListAPI},
        {'name': 'azure', 'title': 'Microsoft Azure', 'import_list_api': AzureBlobImportStorageListAPI, 'export_list_api': AzureBlobExportStorageListAPI},
        {'name': 'redis', 'title': 'Redis', 'import_list_api': RedisImportStorageListAPI, 'export_list_api': RedisExportStorageListAPI},
        {'name': 'gdriver', 'title': 'Google Drive Storage', 'import_list_api': GDriverImportStorageListAPI, 'export_list_api': GDriverExportStorageListAPI}
    ]

def list_storage():
    return [
        {'name': 's3', 'title': 'AWS S3', 'import_instance': S3ImportStorage, 'export_instance': S3ExportStorage},
        {'name': 'gcs', 'title': 'Google Cloud Storage', 'import_instance': GCSImportStorage, 'export_instance': GCSExportStorage},
        {'name': 'azure', 'title': 'Microsoft Azure', 'import_instance': AzureBlobImportStorage, 'export_instance': AzureBlobExportStorage},
        {'name': 'redis', 'title': 'Redis', 'import_instance': RedisImportStorage, 'export_instance': RedisExportStorage},
        {'name': 'gdriver', 'title': 'Google Drive Storage', 'import_instance': GDriverImportStorage, 'export_instance': GDriverExportStorage}
    ]

def get_all_project_storage(project_id):
    lst_storage_pj = []
    try:
        lst_storage = list_storage()
        for storage in lst_storage:
            import_instance = storage['import_instance']
            filtered_objects = import_instance.objects.filter(project_id=project_id)
            lst_storage_pj.extend(filtered_objects)
    except Exception as e:
        print(e)
    return lst_storage_pj

def get_all_project_storage_with_name(project_id):
    lst_storage_pj = []
    try:
        lst_storage = list_storage()
        for storage in lst_storage:
            import_instance = storage['import_instance']
            filtered_objects = import_instance.objects.filter(project_id=project_id)
            
            # Thêm thông tin 'name' vào từng đối tượng trong filtered_objects
            for obj in filtered_objects:
                obj.storage_name = storage['name']  # Gắn 'name' vào đối tượng
                lst_storage_pj.append(obj)
                
    except Exception as e:
        print(e)
    return lst_storage_pj

def get_storage_by_name(storage_name):
    storages = list_storage()
    # Tìm storage có name trùng với storage_name
    return next((storage for storage in storages if storage['name'] == storage_name), None)
