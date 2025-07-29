from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from projects.models import Project, CrawlHistory
from projects.serializers import ( ProjectAdminViewSerializer)
from rest_framework import  generics, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from core.swagger_parameters import page_parameter, search_parameter, field_search_parameter, sort_parameter, type_parameter
from django_filters.rest_framework import DjangoFilterBackend
from core.permissions import ViewClassPermission, all_permissions
from drf_yasg import openapi
from core.utils.paginate import SetPagination
import requests
from aixblock_core.core.utils.params import get_env
import json
from rest_framework.authtoken.models import Token
from django.utils import timezone
from io_storages.s3.models import S3ImportStorage
@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=['Projects'],
        operation_summary='crawl api',
        operation_description="Crawler api.",
        manual_parameters=[page_parameter, search_parameter, field_search_parameter, sort_parameter, type_parameter, 
                           openapi.Parameter(name='quantity', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY),
                           openapi.Parameter(name='label', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY),
                           openapi.Parameter(name='keyword', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY, required=True),
                           openapi.Parameter(name='all', type=openapi.TYPE_BOOLEAN, in_=openapi.IN_QUERY),
                           openapi.Parameter(name='search_id', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY)
                           ]
        
    ))
class CrawlDataAPI(generics.ListAPIView):
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    permission_required = ViewClassPermission(
        GET=all_permissions.annotations_view,
        POST=all_permissions.annotations_view,
    )
    pagination_class = SetPagination
    filter_backends = [DjangoFilterBackend]
    serializer_class = ProjectAdminViewSerializer

    def get_queryset(self):
        return Project.objects.order_by('-id')

    def get(self, *args, **kwargs):
        from requests.utils import requote_uri
        from core.settings.base import MINIO_API_URL

        try:
            url_docker = get_env('CRAWL_URL', "https://127.0.0.1:5001/")
            data = {
                "type": self.request.query_params.get('type', 'photo'),
                "keyword": requote_uri(self.request.query_params.get('keyword', '')),
                "page": int(self.request.query_params.get('page', 1)),
                "page_size": int(self.request.query_params.get('page_size', 10)),
                "search_id": self.request.query_params.get('search_id', ""),
                "search_all":  self.request.query_params.get('all', "false"),
                "quantity_crawl": int(self.request.query_params.get('quantity', 10)),
                "host_url": get_env('AXB_HOST', "https://172.17.0.1:8080/"),
                "project_id": int(self.request.query_params.get('project_id', 0))
            }

            token = Token.objects.filter(user=self.request.user)
            storage = S3ImportStorage.objects.filter(project_id=data['project_id']).first()
            project_instance = Project.objects.filter(id=data['project_id']).first()
            headers = dict(self.request.headers)
            print("Header send", headers)
            headers = {
                'Content-Type': 'application/json'
            }
            
            headers['token'] = token.first().key
            if storage:
                headers['storage'] = f'{storage.id}'
            if "Origin" in self.request.headers and self.request.headers["Origin"]:
                headers['url'] = self.request.headers["Origin"]
            elif "Host" in self.request.headers:
                headers['url'] = self.request.headers["Host"]
            else:
                headers['url'] = "https://app.aixblock.io/"
            
            if project_instance:
                headers['s3accesskey'] = project_instance.s3_access_key
                headers['s3secretkey'] = project_instance.s3_secret_key
                headers['s3endpoint'] = MINIO_API_URL

            print("craw data")
            print("Header send", headers)
            json_data = json.dumps(data)
            print("json_data", json_data)
            response = requests.post(
                url_docker, data=json_data, headers=headers, verify=False
            )
            print("craw response", response)
            print("url_docker", url_docker)
            print("Response status code:", response.status_code)
            print("Response headers:", response.headers)
            print("Response text:", response.text)
            if response.status_code == 200:
                print("success")
                crawled_data = response.json()
                print("crawled_data", crawled_data)
                if not CrawlHistory.objects.filter(search_id=crawled_data['search_id'], deleted_at__isnull=True):
                    CrawlHistory.objects.filter(project_id=data['project_id']).update(deleted_at=timezone.now())
                    CrawlHistory.objects.create(project_id=data['project_id'], keyword=data['keyword'], type=data['type'], quantity=data['quantity_crawl'], search_id=crawled_data['search_id'])
                return Response(crawled_data, status=status.HTTP_200_OK)
            else:
                # crawled_data = response.json()
                fail_mesage = 'Failed to crawl data'
                # if 'msg' in crawled_data:
                #     fail_mesage = crawled_data['error']
                return Response({'error': fail_mesage}, status=response.status_code)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
