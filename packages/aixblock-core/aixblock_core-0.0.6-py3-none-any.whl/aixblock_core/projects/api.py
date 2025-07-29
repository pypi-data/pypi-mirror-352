"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import io
import json
import logging
import os
import random
import time
import requests
from urllib.parse import urlparse
from django.utils import timezone

import docker
import drf_yasg.openapi as openapi
import requests.auth
from core.filters import ListFilter
from core.label_config import config_essential_data_has_changed, parse_config
from core.permissions import ViewClassPermission, all_permissions
from core.utils.common import (get_object_with_check_and_log, paginator,
                               paginator_help,
                               temporary_disconnect_all_signals)
from core.utils.exceptions import (AIxBlockDatabaseException,
                                   ProjectExistException)
from core.utils.io import find_dir, find_file, read_yaml
from data_manager.functions import (filters_ordering_selected_items_exist,
                                    get_prepared_queryset)
from django.conf import settings
from django.db import IntegrityError
from django.db.models import F, Q, OuterRef
from django.http import FileResponse, Http404, JsonResponse
from django.utils.decorators import method_decorator
from django_filters import FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from ml.models import MLGPU, MLBackend
from projects.functions.next_task import get_next_task
from projects.models import (Project, ProjectCheckpoint,# ProjectCrawlQueue
                             ProjectGPU, ProjectManager, ProjectSummary, ProjectMLPort, CrawlHistory)
from projects.pii_entities import ProjectPiiEntities
from projects.serializers import (DockerSerializer, GetFieldsSerializer,
                                  ProjectLabelConfigSerializer,
                                  ProjectQueueRequest, ProjectSerializer, ListProjectSerializer,
                                  ProjectSummarySerializer, ProjectAdminViewSerializer)
from rest_framework import filters, generics, mixins, status
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import ValidationError as RestValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser, FileUploadParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView, exception_handler
from tasks.models import Task
from tasks.serializers import (
    NextTaskSerializer, TaskSerializer, TaskSimpleSerializer,
    TaskWithAnnotationsAndPredictionsAndDraftsSerializer)
from users.serializers import UserSerializer, UserSimpleSerializer
from webhooks.models import WebhookAction
from webhooks.utils import (api_webhook, api_webhook_for_delete,
                            emit_webhooks_for_instance)
from .labels import ProjectLabels
from .serializers import UploadedFileSerializer, ProjectMLPortSerializer
from core.utils.paginate import SetPagination
from model_marketplace.models import ModelMarketplace
from compute_marketplace.models import ComputeMarketplace, ComputeGPU, ComputeGpuPrice
from django.shortcuts import get_object_or_404
from projects.services.project_api_helper import init_project_cloud_storage, project_upload_file
from projects.services.project_cloud_storage import project_logs_minio
from io_storages.s3.models import S3ImportStorage, S3ExportStorage
from botocore.exceptions import ParamValidationError, ClientError
from core.services.minio_client import MinioClient
from core.settings.base import MINIO_API_URL
from projects.services.project_nginx_proxy import NginxReverseProxyManager
from compute_marketplace.gpu_util import GPUCostCalculator, GPU, map_gpu_to_tflops, map_gpu_to_power_consumption
from organizations.models import Organization, OrganizationMember, Organization_Project_Permission
from core.utils.convert_memory_to_byte import convert_memory_to_byte
from ml.models import MLNetworkHistory, MLNetwork
from aixblock_core.core.utils.nginx_server import NginxReverseProxy
from rest_framework.authtoken.models import Token
from projects.calc_flops_mem import calc_time_neeed_nlp, calc_mem_pytorch_images, calc_time_neeed_pytorch_images, calc_mem_tf, calc_mem_gpu_tf, calc_param_from_tflop, calc_tflop_from_param
from model_marketplace.calc_transformer_mem import config_parser as config_cacl_mem, calc_mem
from ml.models import MLBackend
from orders.models import OrderComputeGPU
from compute_marketplace.plugin_provider import vast_provider
from .function import convert_url, check_url_status, check_dashboard_url_until_available

logger = logging.getLogger(__name__)
HOSTNAME = os.environ.get('HOST', 'https://app.aixblock.io/')
API_KEY = os.environ.get('API_KEY', 'fb5b650c7b92ddb5150b7965b58ba3854c87d94b')
IN_DOCKER = bool(os.environ.get('IN_DOCKER', True))
DOCKER_API = "tcp://108.181.196.144:4243" if IN_DOCKER else "unix://var/run/docker.sock"
NUM_GPUS = int(os.environ.get('NUM_GPUS', 1))
TOTAL_CONTAINERS = int(os.environ.get('TOTAL_CONTAINERS', 50))
INSTALL_TYPE = os.environ.get('INSTALL_TYPE', 'PLATFORM')
IMAGE_TO_SERVICE = {
    'huggingface_image_classification': 'computer_vision/image_classification',
    'huggingface_text_classification': 'nlp/text_classification',
    'huggingface_text2text': 'nlp/text2text',
    'huggingface_text_summarization': 'nlp/text_summarization',
    'huggingface_question_answering': 'nlp/question_answering',
    'huggingface_token_classification': 'nlp/token_classification',
    'huggingface_translation': 'nlp/translation',
}

_result_schema = openapi.Schema(
    title='Labeling result',
    description='Labeling result (choices, labels, bounding boxes, etc.)',
    type=openapi.TYPE_OBJECT,
    properies={
        'from_name': openapi.Schema(
            title='from_name',
            description='The name of the labeling tag from the project config',
            type=openapi.TYPE_STRING
        ),
        'to_name': openapi.Schema(
            title='to_name',
            description='The name of the labeling tag from the project config',
            type=openapi.TYPE_STRING
        ),
        'value': openapi.Schema(
            title='value',
            description='Labeling result value. Format depends on chosen ML backend',
            type=openapi.TYPE_OBJECT
        )
    },
    example={
        'from_name': 'image_class',
        'to_name': 'image',
        'value': {
            'labels': ['Cat']
        }
    }
)

_task_data_schema = openapi.Schema(
    title='Task data',
    description='Task data',
    type=openapi.TYPE_OBJECT,
    example={
        'id': 1,
        'my_image_url': '/static/samples/kittens.jpg'
    }
)


class ProjectListPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'


class ProjectFilterSet(FilterSet):
    ids = ListFilter(field_name="id", lookup_expr="in")


@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Projects'],
    operation_summary='List your projects',
    operation_description="""
    Return a list of the projects that you've created.

    To perform most tasks with the AiXBlock API, you must specify the project ID, sometimes referred to as the `pk`.
    To retrieve a list of your AiXBlock projects, update the following command to match your own environment.
    Replace the domain name, port, and authorization token, then run the following from the command line:
    ```bash
    curl -X GET {}/api/projects/ -H 'Authorization: Token abc123'
    ```
    """.format(settings.HOSTNAME or 'https://localhost:8080')
))
class ListProjectListAPI(generics.ListCreateAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser, FileUploadParser)
    serializer_class = ListProjectSerializer

    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = ProjectFilterSet
    permission_required = ViewClassPermission(
        GET=all_permissions.projects_view,
        POST=all_permissions.projects_create,
    )
    pagination_class = ProjectListPagination

    def get_queryset(self):
     

        serializer = GetFieldsSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        fields = serializer.validated_data.get('include')
        filter = serializer.validated_data.get('filter')

        projects = Project.objects.filter(
            organization=self.request.user.active_organization
            # Q(organization_id__in=organization_join)
        ).order_by(F('pinned_at').desc(nulls_last=True), "-created_at")

        org_member = OrganizationMember.objects.filter(user_id=self.request.user.id, organization=self.request.user.active_organization).first()
        if org_member:
            if self.request.user.is_superuser==False and org_member.is_admin==False and org_member.level_org==False:
                project_join = Organization_Project_Permission.objects.filter(organization=self.request.user.active_organization, user_id=self.request.user.id).values_list("project_id", flat=True)
                if project_join:
                    projects = projects.filter(id__in=project_join)

        projects = projects.filter(~Q(label_config="<Draft/>"))
        if filter in ['pinned_only', 'exclude_pinned']:
            projects = projects.filter(pinned_at__isnull=filter == 'exclude_pinned')
        return ProjectManager.with_counts_annotate(projects, fields=fields).prefetch_related('members', 'created_by')

    def get_serializer_context(self):
        context = super(ListProjectListAPI, self).get_serializer_context()
        context['created_by'] = self.request.user
        return context

    def get(self, request, *args, **kwargs):
        return super(ListProjectListAPI, self).get(request, *args, **kwargs)

@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Projects'],
    operation_summary='Create new project',
    operation_description="""
    Create a project and set up the labeling interface in AiXBlock using the API.

    ```bash
    curl -H Content-Type:application/json -H 'Authorization: Token abc123' -X POST '{}/api/projects' \
    --data '{{"label_config": "<View>[...]</View>"}}'
    ```
    """.format(settings.HOSTNAME or 'https://localhost:8080'),
))
class ProjectListAPI(generics.ListCreateAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser, FileUploadParser)
    serializer_class = ProjectSerializer

    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = ProjectFilterSet
    permission_required = ViewClassPermission(
        GET=all_permissions.projects_view,
        POST=all_permissions.projects_create,
    )
    pagination_class = ProjectListPagination

    def get_queryset(self):
        serializer = GetFieldsSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        fields = serializer.validated_data.get('include')
        filter = serializer.validated_data.get('filter')
        # organization_join = OrganizationMember.objects.filter(user_id=self.request.user.id).values_list("organization_id", flat = True)
        
        projects = Project.objects.filter(
            organization=self.request.user.active_organization
            # Q(organization_id__in=organization_join)
        ).order_by(F('pinned_at').desc(nulls_last=True), "-created_at")

        projects = projects.filter(~Q(label_config="<Draft/>"))
        if filter in ['pinned_only', 'exclude_pinned']:
            projects = projects.filter(pinned_at__isnull=filter == 'exclude_pinned')
        return ProjectManager.with_counts_annotate(projects, fields=fields).prefetch_related('members', 'created_by')

    def get_serializer_context(self):
        context = super(ProjectListAPI, self).get_serializer_context()
        context['created_by'] = self.request.user
        return context

    def perform_create(self, ser):
        # if not staff
        # if not self.request.user.is_staff:
        #     if len(Project.objects.filter(organization=self.request.user.active_organization)) > 1:
        #         raise AIxBlockDatabaseException('You have reached the projects count limit.')

        try:
            organiztion = Organization.objects.filter(pk = self.request.user.active_organization_id).first()
            organiztion_member = OrganizationMember.objects.filter(organization=organiztion, is_admin=True)
            if self.request.user.is_superuser or organiztion_member.exists() or organiztion.created_by_id == self.request.user.id:
                project = ser.save(organization=self.request.user.active_organization)

                def create_storage_prj(project):
                    try:
                        init_project_cloud_storage(project)

                        bucket = f'project-{project.id}'
                        aws_access_key_id = project.s3_access_key
                        aws_secret_access_key = project.s3_secret_key
                        aws_session_token = project.token

                        cloud_client = MinioClient(
                            access_key=project.s3_access_key,
                            secret_key=project.s3_secret_key)
                        
                        cloud_client.create_bucket(
                            bucket_name=bucket
                        )
                        # if project.file:
                        #     project_upload_file(project)

                        data_type =  project.data_types
                        if 'image' in data_type:
                            filter_s3 = "raw_files/.+\.(jpg|png|jpeg)"
                        elif 'audio' in data_type:
                            filter_s3 = "raw_files/.+\.(mp3|ogg)"
                        elif 'video' in data_type:
                            filter_s3 = "raw_files/.+\.(mp4|mp5)"
                        else:
                            filter_s3 = "raw_files/.+\.(txt|csv|json)"

                    
                        # domain_endpoint = "https://"
                        # if INSTALL_TYPE == "SELF-HOST":
                        domain_endpoint = "http://"
                        if not "http" in MINIO_API_URL:
                            end_point = f'{domain_endpoint}{MINIO_API_URL}'
                        # Create Import-Export S3
                        S3ImportStorage.objects.create(bucket=bucket, project_id = project.id, aws_access_key_id = aws_access_key_id, aws_secret_access_key = aws_secret_access_key, s3_endpoint = end_point, aws_session_token = aws_session_token, use_blob_urls=True, regex_filter=filter_s3)
                        S3ExportStorage.objects.create(bucket=bucket, project_id = project.id, aws_access_key_id = aws_access_key_id, aws_secret_access_key = aws_secret_access_key, s3_endpoint = end_point, aws_session_token = aws_session_token)
                    
                    except Exception as e:
                        print(e)
                
                # create_storage_thread = threading.Thread(target=create_storage_prj, args=(project,))
                # create_storage_thread.start()
                # create_storage_thread.join(timeout=10)

                # html_file_path =  './aixblock_labeltool/templates/mail/create_project_success.html'
                # email_member = list(organiztion_member.exclude(user=self.request.user).values_list('user__email', flat=True))
                # with open(html_file_path, 'r', encoding='utf-8') as file:
                #     html_content = file.read()

                # data = {
                #     "subject": "Welcome to AIxBlock - Registration Successful!",
                #     "from": "noreply@aixblock.io",
                #     "to": email_member,
                #     "html": html_content,
                #     "text": "Welcome to AIxBlock!",
                #     "attachments": []
                # }

                # # def send_email_thread(data):
                # #     notify_reponse.send_email(data)

                # # Start a new thread to send email
                # docket_api = "tcp://69.197.168.145:4243"
                # host_name = '69.197.168.145'

                # email_thread = threading.Thread(target=send_email_thread, args=(docket_api, host_name, data,))
                # email_thread.start()
                
                # try:
                #     storage.validate_connection()
                # except ParamValidationError as e:
                #     print(e)
                # except ClientError as e:
                #     print(e)
            else:
                raise AIxBlockDatabaseException("You do not have permission to create project", code=status.HTTP_403_FORBIDDEN)

        except IntegrityError as e:
            if str(e) == 'UNIQUE constraint failed: project.title, project.created_by_id':
                raise ProjectExistException('Project with the same name already exists: {}'.
                                            format(ser.validated_data.get('title', '')))
            raise AIxBlockDatabaseException('Database error during project creation. Try again.')

    def get(self, request, *args, **kwargs):
        return super(ProjectListAPI, self).get(request, *args, **kwargs)

    @api_webhook(WebhookAction.PROJECT_CREATED)
    def post(self, request, *args, **kwargs):

        return super(ProjectListAPI, self).post(request, *args, **kwargs)

@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=['Projects'],
        operation_summary='List projects for Admin',
        operation_description="Return a list of the projects from admin views.",
    ))
class ProjectListAdminViewAPI(generics.ListAPIView):
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    permission_classes = (AllowAny, )
    pagination_class = SetPagination
    serializer_class = ProjectAdminViewSerializer

    def get_queryset(self):
        return Project.objects.order_by('-id')


    def get(self, *args, **kwargs):
        return super(ProjectListAdminViewAPI, self).get(*args, **kwargs)


@method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['Projects'],
        operation_summary='Get project by ID',
        operation_description='Retrieve information about a project by project ID.'
    ))
@method_decorator(name='delete', decorator=swagger_auto_schema(
        tags=['Projects'],
        operation_summary='Delete project',
        operation_description='Delete a project by specified project ID.'
    ))
@method_decorator(name='patch', decorator=swagger_auto_schema(
        tags=['Projects'],
        operation_summary='Update project',
        operation_description='Update the project settings for a specific project.',
        request_body=ProjectSerializer
    ))
class ProjectAPI(generics.RetrieveUpdateDestroyAPIView):

    parser_classes = (JSONParser, FormParser, MultiPartParser)
    queryset = Project.objects.with_counts()
    permission_required = ViewClassPermission(
        GET=all_permissions.projects_view,
        DELETE=all_permissions.projects_delete,
        PATCH=all_permissions.projects_change,
        PUT=all_permissions.projects_change,
        POST=all_permissions.projects_create,
    )
    serializer_class = ProjectSerializer

    redirect_route = 'projects:project-detail'
    redirect_kwarg = 'pk'

    def get_queryset(self):
        serializer = GetFieldsSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        fields = serializer.validated_data.get('include')
        organization_join = OrganizationMember.objects.filter(user_id=self.request.user.id).values_list("organization_id", flat = True)
        return Project.objects.with_counts(fields=fields).filter(Q(organization=self.request.user.active_organization) |
            Q(organization_id__in=organization_join))

    def get(self, request, *args, **kwargs):
        return super(ProjectAPI, self).get(request, *args, **kwargs)

    @api_webhook_for_delete(WebhookAction.PROJECT_DELETED)
    def delete(self, request, *args, **kwargs):
        project_id = kwargs.get('pk')   
        project_instance = Project.objects.filter(pk=project_id).first()
        try:
            from ml.models import MLBackend, MLGPU, MLBackendStatus
            from model_marketplace.models import History_Rent_Model

            ml_backends = MLBackend.objects.filter(project_id=project_id, deleted_at__isnull=True)
            for ml_backend in ml_backends:
                ml_gpus = MLGPU.objects.filter(ml_id=ml_backend.id)
                for ml_gpu in ml_gpus:
                    if MLBackend.objects.filter(id = ml_gpu.ml_id, is_deploy = False, deleted_at__isnull=True).exists():
                        MLBackendStatus.objects.filter(ml_id=ml_gpu.ml_id).update(deleted_at=timezone.now())
                        History_Rent_Model.objects.filter(model_id=ml_gpu.model_id).update(status=History_Rent_Model.Status.COMPLETED)
                        ml_backend.deleted_at = timezone.now()
                        ml_gpu.deleted_at = timezone.now()
                        ml_gpu.save()
                ml_backend.save()
        except Exception as e:
            print(e)
            
        if project_instance.organization.created_by_id == self.request.user.id or self.request.user.is_superuser:
            return super(ProjectAPI, self).delete(request, *args, **kwargs)
        else:
            return Response("You do not have permission to delete this data", status=status.HTTP_403_FORBIDDEN)

    @api_webhook(WebhookAction.PROJECT_UPDATED)
    def patch(self, request, *args, **kwargs):
        # if request.data.get('epochs') is not None and request.data.get('epochs') > 10:
        #     raise AIxBlockDatabaseException('The epochs value can not larger than 10')

        # if request.data.get('batch_size') is not None and request.data.get('batch_size') > 16:
        #     raise AIxBlockDatabaseException('The batch size value can not larger than 16')

        if (request.data.get('image_width') is not None and request.data.get('image_width') > 640)\
                or (request.data.get('image_height') is not None and request.data.get('image_height') > 640):
            raise AIxBlockDatabaseException('The image dimension can not larger than 640 x 640')
        
        project = self.get_object()
        check_org_admin = OrganizationMember.objects.filter(organization_id = project.organization_id, user_id=self.request.user.id, is_admin=True).exists()
        if not check_org_admin:
            if not project.organization.created_by_id == self.request.user.id and not self.request.user.is_superuser:
                raise AIxBlockDatabaseException("You do not have permission to setup this project", code=status.HTTP_403_FORBIDDEN)
        
        label_config = self.request.data.get('label_config')
        label_config_title = self.request.data.get('template_name')

        if label_config_title:
            project.label_config_title = label_config_title
            project.save()

        has_changes = False
            
        if label_config:
            try:
                has_changes = config_essential_data_has_changed(label_config, project.label_config)
            except KeyError:
                pass

        return super(ProjectAPI, self).patch(request, *args, **kwargs)

    def perform_create(self, serializer):
        return super(ProjectAPI, self).perform_create(serializer)

    def perform_destroy(self, instance):
        # we don't need to relaculate counters if we delete whole project
        with temporary_disconnect_all_signals():
            instance.delete()

    @swagger_auto_schema(auto_schema=None)
    @api_webhook(WebhookAction.PROJECT_UPDATED)
    def put(self, request, *args, **kwargs):
        return super(ProjectAPI, self).put(request, *args, **kwargs)

@method_decorator(name='patch', decorator=swagger_auto_schema(
        tags=['Projects'],
        operation_summary='Upload file to project by ID',
        operation_description='Upload file to project by ID.',
        manual_parameters=[
            openapi.Parameter('file', openapi.IN_FORM, type=openapi.TYPE_FILE, description='Document to be uploaded'),
        ],
    ))
class ProjectUploadFileApi(APIView):
    parser_classes = MultiPartParser, FileUploadParser
    permission_required = all_permissions.projects_change
    redirect_kwarg = 'pk'
    def patch(self, request, *args, **kwargs):
        instance = Project.objects.get(pk=kwargs['pk'])
        file_serializer = UploadedFileSerializer(instance=instance, data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            # project_upload_file(instance)
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Projects'],
    operation_summary='Get next task to label',
    operation_description="""
    Get the next task for labeling. If you enable Machine Learning in
    your project, the response might include a "predictions"
    field. It contains a machine learning prediction result for
    this task.
    """,
    responses={200: TaskWithAnnotationsAndPredictionsAndDraftsSerializer()}
    ))  # leaving this method decorator info in case we put it back in swagger API docs
class ProjectNextTaskAPI(generics.RetrieveAPIView):

    permission_required = all_permissions.tasks_view
    serializer_class = TaskWithAnnotationsAndPredictionsAndDraftsSerializer  # using it for swagger API docs
    queryset = Project.objects.all()
    swagger_schema = None # this endpoint doesn't need to be in swagger API docs

    def get(self, request, *args, **kwargs):
        project = self.get_object()
        dm_queue = filters_ordering_selected_items_exist(request.data)
        prepared_tasks = get_prepared_queryset(request, project)

        next_task, queue_info = get_next_task(request.user, prepared_tasks, project, dm_queue)

        if next_task is None:
            raise NotFound(
                f'There are still some tasks to complete for the user={request.user}, '
                f'but they seem to be locked by another user.')

        # serialize task
        context = {'request': request, 'project': project, 'resolve_uri': True, 'annotations': False}
        serializer = NextTaskSerializer(next_task, context=context)
        response = serializer.data

        response['queue'] = queue_info
        return Response(response)


@method_decorator(name='post', decorator=swagger_auto_schema(
        tags=['Projects'],
        operation_summary='Validate label config',
        operation_description='Validate an arbitrary labeling configuration.',
        responses={204: 'Validation success'},
        request_body=ProjectLabelConfigSerializer,
    ))
class LabelConfigValidateAPI(generics.CreateAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_classes = (AllowAny,)
    serializer_class = ProjectLabelConfigSerializer

    def post(self, request, *args, **kwargs):
        return super(LabelConfigValidateAPI, self).post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except RestValidationError as exc:
            context = self.get_exception_handler_context()
            response = exception_handler(exc, context)
            response = self.finalize_response(request, response)
            return response

        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(name='post', decorator=swagger_auto_schema(
        tags=['Projects'],
        operation_summary='Validate project label config',
        operation_description="""
        Determine whether the label configuration for a specific project is valid.
        """,
        manual_parameters=[
            openapi.Parameter(
                name='id',
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_PATH,
                description='A unique integer value identifying this project.'),
        ],
        request_body=ProjectLabelConfigSerializer,
))
class ProjectLabelConfigValidateAPI(generics.RetrieveAPIView):
    """ Validate label config
    """
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    serializer_class = ProjectLabelConfigSerializer
    permission_required = all_permissions.projects_change
    queryset = Project.objects.all()

    def post(self, request, *args, **kwargs):
        project = self.get_object()
        label_config = self.request.data.get('label_config')
        if not label_config:
            raise RestValidationError('Label config is not set or is empty')

        # check new config includes meaningful changes
        has_changed = config_essential_data_has_changed(label_config, project.label_config)
        project.validate_config(label_config, strict=True)
        return Response({'config_essential_data_has_changed': has_changed}, status=status.HTTP_200_OK)

    @swagger_auto_schema(auto_schema=None)
    def get(self, request, *args, **kwargs):
        return super(ProjectLabelConfigValidateAPI, self).get(request, *args, **kwargs)


class ProjectSummaryAPI(generics.RetrieveAPIView):
    parser_classes = (JSONParser,)
    serializer_class = ProjectSummarySerializer
    permission_required = all_permissions.projects_view
    queryset = ProjectSummary.objects.all()

    @swagger_auto_schema(auto_schema=None)
    def get(self, *args, **kwargs):
        return super(ProjectSummaryAPI, self).get(*args, **kwargs)


@method_decorator(name='delete', decorator=swagger_auto_schema(
        tags=['Projects'],
        operation_summary='Delete all tasks',
        operation_description='Delete all tasks from a specific project.',
        manual_parameters=[
            openapi.Parameter(
                name='id',
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_PATH,
                description='A unique integer value identifying this project.'),
        ],
))
@method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['Projects'],
        operation_summary='List project tasks',
        operation_description="""
            Retrieve a paginated list of tasks for a specific project. For example, use the following cURL command:
            ```bash
            curl -X GET {}/api/projects/{{id}}/tasks/?page=1&page_size=10 -H 'Authorization: Token abc123'
            ```
        """.format(settings.HOSTNAME or 'https://localhost:8080'),
        manual_parameters=[
            openapi.Parameter(
                name='id',
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_PATH,
                description='A unique integer value identifying this project.'),
        ] + paginator_help('tasks', 'Projects')['manual_parameters'],
    ))
class ProjectTaskListAPI(generics.ListCreateAPIView,
                         generics.DestroyAPIView):

    parser_classes = (JSONParser, FormParser)
    queryset = Task.objects.all()
    permission_required = ViewClassPermission(
        GET=all_permissions.tasks_view,
        POST=all_permissions.tasks_change,
        DELETE=all_permissions.tasks_delete,
    )
    serializer_class = TaskSerializer
    redirect_route = 'projects:project-settings'
    redirect_kwarg = 'pk'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TaskSimpleSerializer
        else:
            return TaskSerializer

    def filter_queryset(self, queryset):
        project = generics.get_object_or_404(Project.objects.for_user(self.request.user), pk=self.kwargs.get('pk', 0))
        tasks = Task.objects.filter(project=project)
        page = paginator(tasks, self.request)
        if page:
            return page
        else:
            raise Http404

    def delete(self, request, *args, **kwargs):
        project = generics.get_object_or_404(Project.objects.for_user(self.request.user), pk=self.kwargs['pk'])
        task_ids = list(Task.objects.filter(project=project).values('id'))
        Task.delete_tasks_without_signals(Task.objects.filter(project=project))
        project.summary.reset()
        emit_webhooks_for_instance(request.user.active_organization, None, WebhookAction.TASKS_DELETED, task_ids)
        return Response(data={'tasks': task_ids}, status=204)

    def get(self, *args, **kwargs):
        return super(ProjectTaskListAPI, self).get(*args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def post(self, *args, **kwargs):
        return super(ProjectTaskListAPI, self).post(*args, **kwargs)

    def get_serializer_context(self):
        context = super(ProjectTaskListAPI, self).get_serializer_context()
        context['project'] = get_object_with_check_and_log(self.request, Project, pk=self.kwargs['pk'])
        return context

    def perform_create(self, serializer):
        project = get_object_with_check_and_log(self.request, Project, pk=self.kwargs['pk'])
        instance = serializer.save(project=project)
        emit_webhooks_for_instance(self.request.user.active_organization, project, WebhookAction.TASKS_CREATED, [instance])

# @method_decorator(name="get", decorator=swagger_auto_schema(
#         tags=['Project TemplateList'],
#         operation_summary='Receive TemplateList',
#         operation_description="""
#         ```bash
#         curl -X POST {}/api/templates -H 'Authorization: Token abc123'
#         ```
#         """.format(settings.HOSTNAME or 'https://localhost:8080')
#     ))
# class TemplateListAPI(generics.ListAPIView):
#     parser_classes = (JSONParser, FormParser, MultiPartParser)
#     permission_required = all_permissions.projects_view
#     # swagger_schema = None

#     def get(self, *args, **kwargs):
#         return super(TemplateListAPI, self).get(*args, **kwargs)
#     def list(self, request, *args, **kwargs):
#         annotation_templates_dir = find_dir('annotation_templates')
#         configs = []
#         for config_file in pathlib.Path(annotation_templates_dir).glob('**/*.yml'):
#             config = read_yaml(config_file)
#             if settings.VERSION_EDITION == 'Community':
#                 if settings.VERSION_EDITION.lower() != config.get('type', 'community'):
#                     continue
#             if config.get('image', '').startswith('/static') and settings.HOSTNAME:
#                 # if hostname set manually, create full image urls
#                 config['image'] = settings.HOSTNAME + config['image']
#             data_type = config.get('group', '').lower()
#             base_image = f"wowai/{data_type.replace(' ', '_')}"
#             if data_type == "computer vision":
#                 config['value'] = 'computer_vision'
#                 # config['url'] = f'{HOSTNAME}:9090'
#                 if config.get('title', '') == "Video Classification" or config.get('title', '') == "Video Object Tracking" or config.get('title', '') == "Image Captioning" or config.get('title', '') == "Image Classification" or config.get('title', '') == "Object Detection with Bounding Boxes":
#                     config['url'] = f'{HOSTNAME}:8027'
#                     base_image = f"wowai/yolov8_bbox"
#                 elif config.get('title', '') == "Video Timeline Segmentation" or config.get('title', '') == "Semantic Segmentation with Masks" or config.get('title', '') == "Semantic Segmentation with Polygons" or config.get('title', '') == "Inventory Tracking" or config.get('title', '') == "Visual Question Answering" :
#                     config['url'] = f'{HOSTNAME}:8028'
#                     base_image = f"wowai/yolov8_polygon"
#                 # elif config.get('title', '') == "Optical Character Recognition":
#                 #     config['url'] = f'{HOSTNAME}:8019'
#                 #     base_image = f"wwowai/tesseract_server"
#             elif data_type == "yolov8":
#                 config['value'] = 'yolov8'
#                 # config['url'] = f'{HOSTNAME}:9090'
#                 if config.get('title', '') == "Object Detection with Bounding Boxes":
#                     config['url'] = f'{HOSTNAME}:8027'
#                     base_image = f"wowai/yolov8_bbox"
#                 elif config.get('title', '') == "Semantic Segmentation with Masks" or config.get('title', '') == "Semantic Segmentation with Polygons" :
#                     config['url'] = f'{HOSTNAME}:8028'
#                     base_image = f"wowai/yolov8_polygon"
#             elif data_type == "detectron2":
#                 config['value'] = 'detectron2'
#                 # config['url'] = f'{HOSTNAME}:9090'
#                 if config.get('title', '') == "Semantic Segmentation with Masks" or config.get('title', '') == "Semantic Segmentation with Polygons" :
#                     config['url'] = f'{HOSTNAME}:8016'
#                     base_image = f"wowai/detectron2_polygon"
#                 base_image = f"wowai/detectron2"
#             elif data_type == "segment anything":
#                 config['value'] = 'segment_anything'
#                 config['url'] = f'{HOSTNAME}:8021'
#                 if config.get('title', '') == "Semantic Segmentation with Masks" or config.get('title', '') == "Semantic Segmentation with Polygons" :
#                     config['url'] = f'{HOSTNAME}:8029'
#                 base_image = f"wowai/segment_anything"
#             elif data_type == "huggingface computer vision":
#                 config['value'] = 'huggingface'
#                 config['url'] = f'{HOSTNAME}:8017'
#                 if config.get('title', '') == "Huggingface Image Classification" or config.get('title', '') == "Huggingface Object Detection" :
#                     config['url'] = f'{HOSTNAME}:8030'
#                 base_image = f"wowai/huggingface-computer-vision"
#             elif data_type == "huggingface nlp":
#                 config['value'] = 'huggingface'
#                 config['url'] = f'{HOSTNAME}:8031'
#                 if data_type == "Huggingface Question Answering":
#                     config['url'] = '{HOSTNAME}:8031'
#                 elif data_type == "Huggingface Text Classification":
#                     config['url'] = f'{HOSTNAME}:8032'
#                 elif data_type == "Huggingface Text Summarization":
#                     config['url'] = f'{HOSTNAME}:8033'
#                 elif data_type == "Huggingface Translation":
#                     config['url'] = f'{HOSTNAME}:8034'
#                 base_image = f"wowai/huggingface-nlp"
#             elif data_type == "large language model":
#                 config['value'] = 'large-language-model'
#                 config['url'] = f'{HOSTNAME}:8018'
#                 # if config.get('title', '') == "Bloom Lora":
#                 #     config['url'] = f'{HOSTNAME}:8013'
#                 #     base_image = f"wowai/bloom_lora"
#                 # el
#                 if config.get('title', '') == "Llama Meta 2":
#                     config['url'] = f'{HOSTNAME}:8018'
#                 base_image = f"wowai/llama_meta_2"
#             elif data_type == "3d model":
#                 config['value'] = '3d-model'
#                 # config['url'] = f'{HOSTNAME}:9090'
#                 # if config.get('title', '') == "3D reconstruction from multiple images":
#                 #     config['url'] = f'{HOSTNAME}:9090'
#                 #     base_image = f"wowai/bloom_lora"
#                 # elif config.get('title', '') == "LLAMA 2":
#                 #     config['url'] = f'{HOSTNAME}:9094'
#                 #     base_image = f"wowai/llama2"
#             elif data_type == "natural language processing":
#                 config['value'] = 'nlp'
#                 # if config.get('title', '') == "Text Classification" :
#                 #     config['url'] = f'{HOSTNAME}:8022'
#                 # elif config.get('title', '') == "Text Summarization":
#                 #     config['url'] = f'{HOSTNAME}:8023'
#                 # elif config.get('title', '') == "Question Answering":
#                 #     config['url'] = f'{HOSTNAME}:8024'  # for predict only
#             elif data_type == "audio/speech processing":
#                 config['value'] = data_type.replace(" ", "_")
#                 if config.get('title', '') == "Automatic Speech Recognition" :
#                     config['url'] = '{HOSTNAME}:8010'
#                     base_image = f"wowai/automatic_speech_recognition"
#                 elif config.get('title', '') == "Automatic Speech Recognition using Segments":
#                     config['url'] = f'{HOSTNAME}:8012'
#                     base_image = f"wowai/wowai/automatic_speech_recognition_using_segments"
#             else:
#                 config['value'] = data_type.replace(" ", "_")
#             config['base_image'] = f"{base_image}:{config.get('version', 'latest')}"

#             configs.append(config)
#         template_groups_file = find_file(os.path.join('annotation_templates', 'groups.txt'))
#         with open(template_groups_file, encoding='utf-8') as f:
#             groups = f.read().splitlines()
#         logger.debug(f'{len(configs)} templates found.')
#         return Response({'templates': configs, 'groups': groups})

class ProjectSampleTask(generics.RetrieveAPIView):
    parser_classes = (JSONParser,)
    queryset = Project.objects.all()
    permission_required = all_permissions.projects_view
    serializer_class = ProjectSerializer
    swagger_schema = None

    def post(self, request, *args, **kwargs):
        label_config = self.request.data.get('label_config')
        if not label_config:
            raise RestValidationError('Label config is not set or is empty')

        project = self.get_object()
        return Response({'sample_task': project.get_sample_task(label_config)}, status=200)


class ProjectModelVersions(generics.RetrieveAPIView):
    parser_classes = (JSONParser,)
    swagger_schema = None
    permission_required = all_permissions.projects_view
    queryset = Project.objects.all()

    def get(self, request, *args, **kwargs):
        project = self.get_object()
        return Response(data=project.get_model_versions(with_counters=True))


class ProjectStatisticsAPI(generics.RetrieveAPIView):
    parser_classes = (JSONParser,)
    swagger_schema = None
    permission_required = all_permissions.projects_view
    queryset = Project.objects.all()

    def get_task_queryset(self, queryset):
        return queryset.select_related('project').prefetch_related('annotations', 'predictions')

    def get(self, request, *args, **kwargs):
        project = self.get_object()

        import json

        from core.utils.common import batch
        from data_export.models import DataExport
        from data_export.serializers import ExportDataSerializer
        from django.db.models import Q, Prefetch
        from PIL import Image, ImageOps
        from tasks.models import Task

        def get_image_size(filepath):
            img = Image.open(filepath)
            img = ImageOps.exif_transpose(img)
            return img.size

        def sum_by_key(dicts, key):
            return sum([d[key] for d in dicts])

        def count_items_has_key(dicts, key):
            return len([d for d in dicts if key in d and d[key]])

        query = Task.objects.filter(project=project)
        task_ids = query.values_list('id', flat=True)
        tasks = []
        for _task_ids in batch(task_ids, 1000):
            tasks += ExportDataSerializer(
                self.get_task_queryset(query.filter(id__in=_task_ids)), many=True, expand=['drafts'],
                context={'interpolate_key_frames': False}
            ).data
        logger.debug('Prepare export files')
        export_type = 'JSON'

        export_stream, content_type, filename = DataExport.generate_export_file(
            project, tasks, export_type, False, request.GET
        )

        # read export_stream to json
        export_stream.seek(0)
        export_json = json.load(export_stream)
        export_stream.close()

        # Get current user id
        user_id = request.user.id
        annotated_by_me = 0
        classes = {}

        for task in export_json:
            for annotations in task['annotations']:
                if annotations['completed_by'] == user_id:
                    annotated_by_me += 1
                for result in annotations['result']:
                    if not result.get('classification'):
                        continue
                    if result.get('classification') not in classes:
                        classes[result['classification']] = 0
                    classes[result['classification']] += 1

        # TODO: get image size from local data to get statistics info

        data = {
            "images": {
                "total": len(export_json),
                "annotated": count_items_has_key(export_json, 'annotations'),
                "annotated_by_me": annotated_by_me,
            },
            "annotations": {
                "total": sum_by_key(export_json, 'total_annotations'),
                "cancelled": sum_by_key(export_json, 'cancelled_annotations'),
                "annotated_by_me": annotated_by_me,
            },
            "comments": {
                "total": sum_by_key(export_json, 'comment_count'),
                "unresolved": sum_by_key(export_json, 'unresolved_comment_count'),
            },
            "predictions": {
                "total": sum_by_key(export_json, 'total_predictions'),
            },
            "labels": classes
        }
        return Response(data=data)

@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Projects Docker'],
    operation_summary='List project\'s docker containers',
    operation_description="""
    Return a list of current project's docker containers.
    ```bash
    curl -X GET {}/api/projects/<int:pk>/docker/ -H 'Authorization: Token abc123'
    ```
    """.format(settings.HOSTNAME or 'https://localhost:8080')
))
@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Projects Docker'],
    operation_summary='Create new docker container with specific service',
    operation_description="""
    For example, to create a container with base_image `wowai/text_classification`, post the following data:
    {{"base_image": "wowai/text_classification"}}

    Response: the created container's id.

    ```bash
    curl -H Content-Type:application/json -H 'Authorization: Token abc123' -X POST '{}/api/projects/<int:pk>/docker/' \
    --data '{{"base_image": "wowai/text_classification"}}'
    ```
    """.format(settings.HOSTNAME or 'https://localhost:8080')
))
@method_decorator(name='put', decorator=swagger_auto_schema(
    tags=['Projects Docker'],
    operation_summary='Restart docker container',
    operation_description="""
    Restart a docker container with specific id.

    ```bash
    curl -H Content-Type:application/json -H 'Authorization: Token abc123' -X PUT '{}/api/projects/<int:pk>/docker/' \
    --data '{{"container_id": "container_id"}}"'
    ```
    """.format(settings.HOSTNAME or 'https://localhost:8080')
))
class ProjectDockerAPI(generics.GenericAPIView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    parser_classes = (JSONParser,)
    permission_required = all_permissions.projects_view
    queryset = Project.objects.all()
    serializer_class = DockerSerializer

    def get(self, request, *args, **kwargs):
        # List all containers for this project
        client = docker.DockerClient(base_url=DOCKER_API)
        containers = client.containers.list(filters={'name': f"project-{self.kwargs['pk']}_*"}, all=True)
        if not containers:
            return Response(data=[])
        res = []
        for con in containers:
            ports = {
                "tensorboard_port": "",
                "api_port": "",
            }
            for port in con.attrs['NetworkSettings']['Ports']:
                if port == '6006/tcp':
                    tensorboard_port = ports[port][0]['HostPort']
                    ports['tensorboard_port'] = tensorboard_port
                if port == '9090/tcp':
                    api_port = ports[port][0]['HostPort']
                    ports['api_port'] = api_port
            res.append({
                'id': con.id,
                'name': con.name,
                'status': con.status,
                'ports': ports,
                'created': con.attrs['Created'],
                'image': con.attrs['Config']['Image'],
            })
        client.close()
        return Response(data=res)

    def post(self, request, *args, **kwargs):
        # Create a new container for this project
        client = docker.DockerClient(base_url=DOCKER_API)
        # team_id = self.request.user.team_id
        # get service string from POST request data
        base_image = request.data.get('base_image')
        gpu = request.data.get('gpu')
        print("gpu:{gpu}")
        service = None
        if not base_image:
            raise RestValidationError('Base image is not set or is empty')
        if "huggingface" in base_image:
            if base_image in IMAGE_TO_SERVICE:
                service = IMAGE_TO_SERVICE[base_image]

        container_name = f"project-{self.kwargs['pk']}_{service.replace('/', '-').replace(':', '-')}"
        gpu_id = 0
        # list all docker containers contains GPU_ID in name
        gpus = [i for i in range(NUM_GPUS)]
        random.shuffle(gpus)
        # gpus = ["0"]
        for i in gpus:
            gpu_containers = client.containers.list(filters={'name': f"*GPU{i}*"})
            if len(gpu_containers) >= TOTAL_CONTAINERS:
                # exceed max container for this GPU
                continue
            # assign GPU_ID to container name
            container_name += f"_GPU{i}"
            gpu_id = i
            break

        # check if container name is already exists
        try:
            # create container from service
            # for training only
            container = client.containers.run(
                service,
                detach=True,
                name=container_name,
                device_requests=[
                    docker.types.DeviceRequest(device_ids=[str(gpu_id)], capabilities=[['gpu']])],
                ports={
                    '9090/tcp': None,
                    '6006/tcp': None,
                },
                environment={
                    "IN_DOCKER": "True",
                    "HOST": f"{HOSTNAME}",
                    "API_KEY" :  f"{API_KEY}",
                    "REDIS_HOST": "redis",
                    "REDIS_PORT": 6379,
                    "SERVICE": service,
                },
                volumes={
                    "/data/ml-backend/data/": {
                        'bind': '/data',
                        'mode': 'Z',
                    },
                    "/data/models": {
                        "bind": "/models",
                        "mode": "Z",
                    },
                    "/data/datasets": {
                        "bind": "/datasets",
                        "mode": "Z",
                    }
                }
            )
            # Check if GPU have available memory for this container
            # Example: Each GPU has 24GB can host max 10 containers
            # Each team can have 1 dataset and 1 container, members should use the same container
            # Export specific port for each container
            client.close()
            return Response(data=container.id)
        except Exception as e:
            print(e)
            client.close()
            return Response(f"Container {container_name} already exists", status=400)

    def put(self, request, *args, **kwargs):
        # Restart a container for this project
        client = docker.DockerClient(base_url=DOCKER_API)
        # get service string from POST request data
        container_id = request.data.get('container_id')
        if not container_id:
            raise RestValidationError('Container ID is not set or is empty')
        # if container name is not from this project, raise error
        try:
            container = client.containers.get(container_id)
        except Exception as e:
            raise RestValidationError('Container not found')
        # if not container.name.startswith(f"project-{self.kwargs['pk']}"):
        #     raise RestValidationError('Container ID is not from this project')
        # restart container
        container.restart()
        client.close()
        return Response(data=container.id)

    @swagger_auto_schema(
        tags=['Projects Docker'],
        operation_summary='Delete docker container',
        operation_description="""
        Delete a docker container with specific id.

        ```bash
        curl -H Content-Type:application/json -H 'Authorization: Token abc123' -X DELETE '{}/api/projects/<int:pk>/docker/' \
        --data '{{"container_id": "container_id"}}"'
        ```
        """.format(settings.HOSTNAME or 'https://localhost:8080'),
        request_body=DockerSerializer
    )
    def delete(self, request, *args, **kwargs):
        # Delete a container for this project
        client = docker.DockerClient(base_url=DOCKER_API)
        container_id = request.data.get('container_id')
        if not container_id:
            raise RestValidationError('Container ID is not set or is empty')
        # if container name is not from this project, raise error
        container = client.containers.get(container_id)
        if not container.name.startswith(f"project-{self.kwargs['pk']}"):
            raise RestValidationError('Container ID is not from this project')
        # stop container
        container.stop()
        # delete container
        container.remove(force=True)
        client.close()
        return Response(data=container.id)

@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Projects Docker'],
    operation_summary='List project\'s docker images',
    operation_description="""
    Return a list of current project's docker images.
    ```bash
    curl -X GET {}/api/projects/<int:pk>/docker/ -H 'Authorization: Token abc123'
    ```
    """.format(settings.HOSTNAME or 'https://localhost:8080')
))
class ProjectDockerImageAPI(generics.GenericAPIView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    parser_classes = (JSONParser,)
    permission_required = all_permissions.projects_view
    queryset = Project.objects.all()
    serializer_class = DockerSerializer
    def get(self, request, *args, **kwargs):
        client = docker.DockerClient(base_url=DOCKER_API)
        images = client.images.list()
        # images = client.images.list(filters={'name': f"project-{self.kwargs['pk']}_*"}, all=True)

        if not images:
            return Response(data=[])

        res = []
        for image in images:
            image_name = ""

            if image.attrs['RepoTags']:
                image_name = image.attrs['RepoTags'][0]

            res.append({
            'id': image.id,
            'tags': image.tags,
            'created': image.attrs['Created'], 
            'size': image.attrs['Size'],
            'image': image_name
            })

        client.close()
        return Response(data=res)


@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Projects Docker'],
    operation_summary='List project\'s docker container',
    manual_parameters=[
        openapi.Parameter(
            'container_id',
            in_=openapi.IN_PATH, 
            type=openapi.TYPE_STRING,
            description="ID of the image"
        )
    ],
    operation_description="""
    Return a list of current project's docker images.
    ```bash
    curl -X GET {}/api/projects/<int:pk>/docker/ -H 'Authorization: Token abc123'
    ```
    """.format(settings.HOSTNAME or 'https://localhost:8080')
))
class ProjectDockerContainerAPI(generics.GenericAPIView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    parser_classes = (JSONParser,)
    permission_required = all_permissions.projects_view
    queryset = Project.objects.all()
    serializer_class = DockerSerializer
    def get(self, request, container_id, *args, **kwargs):

        client = docker.DockerClient(base_url=DOCKER_API)

        try:
            container = client.containers.get(container_id)
        except NotFound:
            raise NotFound("Container not found")

        # Check container belongs to project
        # if not container.name.startswith(f"project-{self.kwargs['pk']}"):
        #     raise ValidationError("Container not from this project")

        # Extract ports
        ports = container.attrs['NetworkSettings']['Ports']
        host_ports = {}

        if ports:
            for port, port_mappings in ports.items():
                host_port = port_mappings[0]['HostPort']  
                host_ports[port] = host_port

        data = {
            'id': container.id,
            'name': container.name,  
            'status': container.status,
            'ports': host_ports,
            'created': container.attrs['Created'],
            'image': container.attrs['Config']['Image'] 
        }

        client.close()
        return Response(data)

@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Projects Tensorboard'],
    operation_summary='Get tensorboard URL',
    manual_parameters=[
        openapi.Parameter(
            'backend_id',
            openapi.IN_QUERY,
            description="ID of the backend to use",
            type=openapi.TYPE_INTEGER,
            required=False
        )
    ],
    operation_description="""
    Return tensorboard URL for this project.

    ```bash
    curl -X GET {}/api/projects/<int:pk>/tensorboard/ -H 'Authorization: Token abc123'
    ```
    """.format(settings.HOSTNAME or 'https://localhost:8080')
))
@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Projects Tensorboard'],
    operation_summary='Start tensorboard for this project',
    operation_description="""
    Start tensorboard for this project if it is not running. Else, return the current tensorboard URL.

    ```bash
    curl -H Content-Type:application/json -H 'Authorization: Token abc123' -X POST '{}/api/projects/<int:pk>/tensorboard/'
    ```
    """.format(settings.HOSTNAME or 'https://localhost:8080')
))
class ProjectTensorboardAPI(generics.GenericAPIView, mixins.RetrieveModelMixin):
    permission_required = all_permissions.projects_view
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get(self, request, *args, **kwargs):
        from ml.models import MLBackend

        project = self.get_object()
        tensorboard_url = ""
        dashboard_url = settings.DASHBOARD_URL
        get_dashboard = False

        # return Response({
        #     "tensorboard_url": tensorboard_url,
        #     "proxy_url": "http://0.0.0.0:9090/",
        #     "dashboard_url": dashboard_url
        # })

        ml_backends = MLBackend.objects.filter(
            project=int(float(project.id)),
            deleted_at__isnull=True,
        ).order_by("?")

        token = Token.objects.filter(user=self.request.user)

        if "backend_id" in request.query_params:
            get_dashboard = True
            ml_backends = ml_backends.filter(id=request.query_params["backend_id"])

        for ml_backend in ml_backends:
            ml = ml_backend
            proxy_url = ml.url
            # ip = re.findall( r'([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{2,4})?',ml.url )
            ml_gpu = MLGPU.objects.filter(ml_id=ml.id, deleted_at__isnull = True).first()


            if ml_gpu:
                _compute = ComputeMarketplace.objects.filter(
                        author_id=self.request.user.id,
                        id=ml_gpu.compute_id,
                        deleted_at__isnull = True
                    ).first()
                
                if get_dashboard:
                    compute_gpu = ComputeGPU.objects.filter(compute_marketplace_id=_compute.id).first()
                    order_compute_gpu = OrderComputeGPU.objects.filter(compute_gpu_id = compute_gpu.id).first()
                    order_id = order_compute_gpu.order_id
                    compute_tag = ''
                    if _compute.type == ComputeMarketplace.Type.PROVIDEREXABIT:
                        compute_tag = 'EXABIT'
                    elif _compute.type == ComputeMarketplace.Type.PROVIDERVAST:
                        compute_tag = 'VAST'
                    try:
                        tag = f"{compute_tag}_{project.created_by.email}_{order_id}_{ml_gpu.folder_run}"
                        dashboard_url = self.generate_public_dashboard(tag)
                        # dashboard_https = convert_url(dashboard_url)
                        # dashboard_url = dashboard_url.replace(settings.DASHBOARD_IP, dashboard_https)
                    except Exception as e:
                        print("Error create dashboard: ",e )
                        dashboard_url = settings.DASHBOARD_IP
                
                # model_instance = ModelMarketplace.objects.filter(id=ml_gpu.model_id).first()
                if _compute:
                    if _compute.type == "MODEL-PROVIDER-VAST":
                        # response_data = vast_service.get_instance_info(_compute.infrastructure_id)
                        try:
                            response_data = vast_provider.info_compute(_compute.infrastructure_id)
                            tensorboard_port = response_data['instances']["ports"]["6006/tcp"][0]["HostPort"]
                            proxy_port = response_data['instances']["ports"]["9090/tcp"][0]["HostPort"]
                            tensorboard_url = f"http://{_compute.ip_address}:{tensorboard_port}"

                            if get_dashboard:
                                ml.get_tensorboard(token.first().key)
                                tensorboard_url = convert_url(tensorboard_url)
                        except:
                            proxy_port = _compute.port
                            tensorboard_url = ""

                        # proxy_url = f"https://{_compute.ip_address}:{proxy_port}"

                    else:
                        client = docker.DockerClient(base_url=f"tcp://{_compute.ip_address}:{_compute.docker_port}")
                        # get container for this project
                        # Enable tensorboard for this project
                        containers = client.containers.list(filters={'name': f"project-{project.id}_*"}, all=True)
                        if len(containers) == 0:
                            raise RestValidationError('No container found for this project')

                        try:
                            nginx_proxy_container = client.containers.list(filters={'name': f"nginx_proxy_{project.id}_*"}, all=True)

                            if len(nginx_proxy_container)==0:
                                nginx_proxy_manager = NginxReverseProxyManager(f"tcp://{_compute.ip_address}:{_compute.docker_port}", project.id, host_name=f'{_compute.ip_address}')
                                proxy_port = nginx_proxy_manager.configure_reverse_proxy(containers)
                            else:
                                proxy_port = nginx_proxy_container[0].ports['80/tcp'][0]['HostPort']
                            # nginx_proxy_manager.remove_nginx_service()
                        except Exception as e:
                            print(e)
                        # get first container
                        container = containers[0]
                        # get tensorboard port
                        tensorboard_port = None

                        # check if tensorboard is running
                        is_enabled = 'tensorboard' in container.exec_run('ps -ef').output.decode('utf-8')
                        if is_enabled:
                            ports = container.attrs['NetworkSettings']['Ports']
                            for port in ports:
                                if port == '6006/tcp':
                                    tensorboard_port = ports[port][0]['HostPort']
                                    break

                        if not tensorboard_port:
                            # start tensorboard
                            container.exec_run(f"tensorboard --logdir /data/{project.id}/training --host 0.0.0.0", detach=True)
                            time.sleep(3)  # wait for tensorboard to start
                            container = client.containers.get(container.id)
                            ports = container.attrs['NetworkSettings']['Ports']
                            for port in ports:
                                if port == '6006/tcp':
                                    tensorboard_port = ports[port][0]['HostPort']
                                    break

                        # get tensorboard URL
                        # schema = "http"
                        # if model_instance and model_instance.schema:
                        #     schema = model_instance.schema

                        tensorboard_url = f"{_compute.ip_address}:{tensorboard_port}"

                        # proxy_url = f"https://{_compute.ip_address }:{proxy_port}"
                        status = check_url_status(tensorboard_url)
                        client.close()
                    
                    if "https" in proxy_url:
                        proxy_url = "https://"+convert_url(proxy_url, True)
                    else:
                        proxy_url = "https://"+convert_url(proxy_url, False)
                        
                    status = check_url_status(proxy_url, 1)

                    if status == 200:
                        break
                else: 
                    tensorboard_url = ""
                    proxy_url = ""
            else:
                tensorboard_url = ""
                proxy_url = ""
            
        if len(ml_backends) == 0:
            host_template = project.template.ml_ip
            port_template = project.template.ml_port

            proxy_url = f"https://{host_template}:{port_template}"
            if get_dashboard:
                # dashboard_https = convert_url(settings.DASHBOARD_IP)
                # dashboard_url = dashboard_url.replace(settings.DASHBOARD_IP, dashboard_https)
                check_dashboard_url_until_available(dashboard_url)
            
            tensorboard_url = ""
            proxy_url = "https://"+convert_url(proxy_url, True)
        
        return Response({
            "tensorboard_url": tensorboard_url,
            "proxy_url": proxy_url,
            "dashboard_url": dashboard_url
        })

    def post(self, request, *args, **kwargs):
        # Enable tensorboard for this project
        project = self.get_object()
        client = docker.DockerClient(base_url=DOCKER_API)
        # get container for this project
        containers = client.containers.list(filters={'name': f"project-{project.id}_*"}, all=True)
        if len(containers) == 0:
            raise RestValidationError('No container found for this project')
        # get first container
        container = containers[0]
        # get tensorboard port
        ports = container.attrs['NetworkSettings']['Ports']
        tensorboard_port = None
        # check if tensorboard is running
        is_enabled = 'tensorboard' in container.exec_run('ps -ef').output.decode('utf-8')
        if is_enabled:
            ports = container.attrs['NetworkSettings']['Ports']
            for port in ports:
                if port == '6006/tcp':
                    tensorboard_port = ports[port][0]['HostPort']
                    break

        # start tensorboard with path /data/{project_id}/training
        if not tensorboard_port:
            container.exec_run(f"tensorboard --logdir /data/{project.id}/training --host 0.0.0.0")

        container = client.containers.get(container.id)
        for port in container.attrs['NetworkSettings']['Ports']:
            if port == '6006/tcp':
                tensorboard_port = container.attrs['NetworkSettings']['Ports'][port][0]['HostPort']
                break
        # get tensorboard URL
        tensorboard_url = f"{settings.HOSTNAME or '108.181.196.144'}:{tensorboard_port}"
        client.close()
        return Response({
            "tensorboard_url": tensorboard_url
        })
    
    def generate_public_dashboard(self, tag):
        print('tag', tag)
        resp = requests.get(f"{settings.DASHBOARD_IP}/api/search?tag={tag}", auth=requests.auth.HTTPBasicAuth(settings.GRAFANA_USERNAME, settings.GRAFANA_PASSWORD))
        dashboard_tags = resp.json()
        dashboard_uid = dashboard_tags[0]["uid"]
        print('dashboard_uid', dashboard_uid)

        url = f"{settings.DASHBOARD_IP}/api/dashboards/uid/{dashboard_uid}/public-dashboards"

        # Headers
        headers = {
            'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
            'accept': 'application/json, text/plain, */*'
        }

        resp = requests.post(url, headers=headers, json={
            "isEnabled": True,
            "share": "public"
        }, auth=requests.auth.HTTPBasicAuth(settings.GRAFANA_USERNAME, settings.GRAFANA_PASSWORD))
        print('resp', resp.json())
        response = requests.get(url, headers=headers, auth=requests.auth.HTTPBasicAuth(settings.GRAFANA_USERNAME, settings.GRAFANA_PASSWORD))

        if response.status_code == 200:
            res = response.json()
            link_url = f'{settings.DASHBOARD_IP}/public-dashboards/{res["accessToken"]}?theme=light'
        else:
            return ''

        return link_url


@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Projects Logs'],
    operation_summary='Get logs for this project',
    operation_description="""
    Return logs for all experiments in this project. Example: ['exp0', 'exp1', 'exp2' ...]

    If you want to download specific experiment logs, ?id=<exp_id> can be used. Then a zip file will be downloaded.

    ```bash
    curl -X GET {}/api/projects/<int:pk>/logs/ -H 'Authorization: Token abc123'
    ```
    """.format(settings.HOSTNAME or 'https://localhost:8080')
))
class ProjectLogsAPI(generics.GenericAPIView, mixins.RetrieveModelMixin):
    permission_required = all_permissions.projects_view
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    # def get(self, request, *args, **kwargs):
    #     project = self.get_object()
    #     project_id = project.id
    #     file_path = self.create_zip(project_id)
    #     # return zip file as response
    #     response = FileResponse(open(file_path, 'rb'))
    #     response['Content-Type'] = 'application/zip'
    #     response['Content-Disposition'] = f'attachment; filename=project_{project_id}_logs.zip'
    #     return response

    # @staticmethod
    # def create_zip(project_id):
    #     import re
    #     import zipfile
    #     path = os.path.join('/data/ml-backend', str(project_id), 'training')
    #     zip_path = f'/tmp/project_{project_id}_logs.zip'
    #     # zip all subfolders, only include .json and .yaml, .txt files
    #     with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive_file:
    #         for root, dirs, files in os.walk(path):
    #             for file in files:
    #                 # include only .json, .txt, .yaml, and  tensorboard files (events.out.tfevents.*)
    #                 if re.match(r'.*\.(json|txt|yaml|png|jpg|md)$', file) or re.match(r'^events.out.tfevents.*', file):
    #                     # write file to zip (with relative path)
    #                     archive_file.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))

    #     return zip_path
    def get(self, request, *args, **kwargs):
        project = self.get_object()
        project_id = project.id
        file_path = self.create_zip(project_id)
        # return zip file as response
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Type'] = 'application/zip'
        response['Content-Disposition'] = f'attachment; filename=project_{project_id}_logs.zip'
        return response
    
    @staticmethod
    def create_zip_name(project_id):
        return f'project_{project_id}_logs.zip'
    
    @staticmethod
    def create_zip(project_id):
        import re
        import zipfile
        path = os.path.join('/data/ml-backend', str(project_id), 'training')
        zip_name = ProjectLogsAPI.create_zip_name(project_id)
        zip_path = f'/tmp/{zip_name}'
        # zip all subfolders, only include .json and .yaml, .txt files
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive_file:
            for root, dirs, files in os.walk(path):
                for file in files:
                    # include only .json, .txt, .yaml, and  tensorboard files (events.out.tfevents.*)
                    if re.match(r'.*\.(json|txt|yaml|png|jpg|md)$', file) or re.match(r'^events.out.tfevents.*', file):
                        # write file to zip (with relative path)
                        archive_file.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))

        return zip_path


@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Projects Logs'],
    operation_summary='Upload project logs',
    operation_description='Upload project logs',
))
class ProjectLogsUploadAPIView(generics.GenericAPIView):
    permission_required = all_permissions.projects_view
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def post(self):
        project = self.get_object()
        project_id = project.id
        file_path = ProjectLogsAPI.create_zip(project_id)
        project_logs_minio.upload_file(
            project=project,
            bucket_name=str(project.id),
            object_name=str(os.path.basename(file_path)),
            file_path=file_path,
        )
        return Response({
            'success': True,
            'message': 'Project logs uploaded started'}, status=status.HTTP_201_CREATED)


@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Projects Logs'],
    operation_summary='Download project logs',
    operation_description='Download project logs',
))
class ProjectLogsDownloadAPIView(generics.GenericAPIView):
    permission_required = all_permissions.projects_view
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    
    def get(self):
        project = self.get_object()
        file_name = ProjectLogsAPI.create_zip_name(project.id)
        project_logs_minio.download_file(
            project=project,
            bucket_name=str(project.id),
            object_name=file_name,
            save_path=file_name
        )
        response = FileResponse(open(file_name, "rb"))
        response['Content-Type'] = 'application/zip'
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        os.remove(file_name)
        return response

@method_decorator(name="post", decorator=swagger_auto_schema(
    tags=['Project Stats'],
    operation_summary='Recalculate stats for this project',
    operation_description="""
    ```bash
    curl -X POST {}/api/projects/<int:pk>/stats/ -H 'Authorization: Token abc123'
    ```
    """.format(settings.HOSTNAME or 'https://localhost:8080')
))
class ProjectStatsAPI(generics.GenericAPIView, mixins.RetrieveModelMixin):
    permission_required = all_permissions.projects_view
    queryset = Project.objects.all()

    def post(self, request, *args, **kwargs):
        project = self.get_object()

        if project.is_audio_project():
            project.update_audio_project_stats()

        project.update_qa_stats()

        return JsonResponse(data=ProjectSerializer(project).data)

@method_decorator(name="get", decorator=swagger_auto_schema(
    tags=['Project Report'],
    operation_summary='Recalculate stats for this project',
    operation_description="""
    ```bash
    curl -X POST {}/api/projects/<int:pk>/stats/ -H 'Authorization: Token abc123'
    ```
    """.format(settings.HOSTNAME or 'https://localhost:8080')
))
class ProjectReportAPI(generics.GenericAPIView, mixins.RetrieveModelMixin):
    permission_required = all_permissions.projects_view
    queryset = Project.objects.all()

    def get(self, request, *args, **kwargs):
        project = self.get_object()
        is_audio_project = project.is_audio_project()
        tasks = Task.objects.filter(project=project)
        stats = dict()
        users = dict()
        total = 0
        total_approved = 0
        total_rejected = 0
        audio_duration = 0.0
        audio_mono_duration = 0.0
        audio_stereo_duration = 0.0
        audio_approved_duration = 0.0
        audio_approved_mono_duration = 0.0
        audio_approved_stereo_duration = 0.0
        audio_rejected_duration = 0.0
        audio_rejected_mono_duration = 0.0
        audio_rejected_stereo_duration = 0.0

        for task in tasks:
            last_annotation = task.annotations.last()

            if last_annotation is None:
                continue

            user_id = last_annotation.completed_by.id

            if user_id not in stats:
                users[user_id] = UserSimpleSerializer(last_annotation.completed_by).data
                stats[user_id] = dict({
                    "tasks": 0,
                    "approved_tasks": 0,
                    "rejected_tasks": 0,
                    "audio_duration": 0,
                    "audio_mono_duration": 0,
                    "audio_stereo_duration": 0,
                    "audio_approved_duration": 0,
                    "audio_approved_mono_duration": 0,
                    "audio_approved_stereo_duration": 0,
                    "audio_rejected_duration": 0,
                    "audio_rejected_mono_duration": 0,
                    "audio_rejected_stereo_duration": 0,
                })

            stats[user_id]["tasks"] = stats[user_id]["tasks"] + 1
            total += 1

            if task.reviewed_result == "approved":
                stats[user_id]["approved_tasks"] += 1
                total_approved += 1
            elif task.reviewed_result == "rejected":
                stats[user_id]["rejected_tasks"] += 1
                total_rejected += 1

            if is_audio_project:
                if not task.is_data_has_audio_meta():
                    task.calculate_audio_meta()

                if "duration" in task.data:
                    duration = round(task.data["duration"], 2)
                else:
                    continue

                is_stereo = "channels" in task.data and task.data["channels"] > 1
                stats[user_id]["audio_duration"] += duration
                audio_duration += duration

                if is_stereo:
                    stats[user_id]["audio_stereo_duration"] += duration
                    audio_stereo_duration += duration
                else:
                    stats[user_id]["audio_mono_duration"] += duration
                    audio_mono_duration += duration

                if task.reviewed_result == "approved":
                    stats[user_id]["audio_approved_duration"] += duration
                    audio_approved_duration += duration

                    if is_stereo:
                        stats[user_id]["audio_approved_stereo_duration"] += duration
                        audio_approved_stereo_duration += duration
                    else:
                        stats[user_id]["audio_approved_mono_duration"] += duration
                        audio_approved_mono_duration += duration

                elif task.reviewed_result == "rejected":
                    stats[user_id]["audio_rejected_duration"] += duration
                    audio_rejected_duration += duration

                    if is_stereo:
                        stats[user_id]["audio_rejected_stereo_duration"] += duration
                        audio_rejected_stereo_duration += duration
                    else:
                        stats[user_id]["audio_rejected_mono_duration"] += duration
                        audio_rejected_mono_duration += duration

        return JsonResponse(data=dict({
            "stats": stats,
            "summary": dict({
                "tasks": total,
                "approved_tasks": total_approved,
                "rejected_tasks": total_rejected,
                "audio_duration": round(audio_duration, 2),
                "audio_mono_duration": round(audio_mono_duration, 2),
                "audio_stereo_duration": round(audio_stereo_duration, 2),
                "audio_approved_duration": round(audio_approved_duration, 2),
                "audio_approved_mono_duration": round(audio_approved_mono_duration, 2),
                "audio_approved_stereo_duration": round(audio_approved_stereo_duration, 2),
                "audio_rejected_duration": round(audio_rejected_duration, 2),
                "audio_rejected_mono_duration": round(audio_rejected_mono_duration, 2),
                "audio_rejected_stereo_duration": round(audio_rejected_stereo_duration, 2),
            }),
            "users": users,
        }))
# @method_decorator(name='get', decorator=swagger_auto_schema(
#         tags=['Project Crawl Queue'],
#         operation_summary='Retrieve my queue',
#         operation_description=''
#     ))
# @method_decorator(
#         name='post',
#         decorator=swagger_auto_schema(
#             tags=['Project Crawl Queue'],
#             operation_summary='',
#             operation_description="""

#             """,
#             manual_parameters=[

#             ],
#             request_body=ProjectQueueRequest,
#             responses={
#                 200: openapi.Response(title='Task queue OK', description='Task queue has succeeded.'),
#             },
#         )
#     )
# class ProjectCrawlQueueAPI(generics.mixins.ListModelMixin,APIView):
#     parser_classes = (JSONParser, FormParser, MultiPartParser)
#     queryset = ProjectCrawlQueue.objects.all()
#     permission_classes = (IsAuthenticated,)
#     serializer_class = UserSerializer
#     def get_queryset(self):
#         return ProjectCrawlQueue.objects.filter()

#     def filter_queryset(self, queryset):
#         return ProjectCrawlQueue.objects.all()

#     def get(self, request, *args, **kwargs):
#         return Response(
#             list(ProjectCrawlQueue.objects.values('id', 'project_id', 'task_id', 'try_count','max_tries','priority','status'))
#         )

#     def post(self, request, *args, **kwargs):
#         j_obj = json.loads(request.body)
#         # print(j_obj )
#         user = request.user
#         if int(j_obj["id"]) > 0:
#             item =ProjectCrawlQueue.objects.filter(id=int(j_obj["id"])).first()
#             item.project_id=j_obj["project_id"]
#             item.status=j_obj["status"]
#             item.try_count=j_obj["try_count"]
#             item.max_tries=j_obj["max_tries"]
#             item.priority=j_obj["priority"]
#             item.save()
#         else:
#             ProjectCrawlQueue.objects.create(
#                     user_id=user.id,
#                     project_id=j_obj["project_id"],
#                     status=j_obj["status"],
#                     try_count=j_obj["try_count"],
#                     max_tries=j_obj["max_tries"],
#                     priority=j_obj["priority"],
#                 )
#         # print(result )
#         return Response({"msg":"done"}, status=200)
# @method_decorator(name='get', decorator=swagger_auto_schema(
#         tags=['Project GPU'],
#         operation_summary='Retrieve GPU',
#         operation_description=''
#     ))
# @method_decorator(name="post", decorator=swagger_auto_schema(
#     tags=['Project GPU'],
#     operation_summary='Recalculate stats for this project',
#     operation_description="""
#     ```bash
#     curl -X POST {}/api/projects/<int:pk>/gpu/ -H 'Authorization: Token abc123'
#     ```
#     """.format(settings.HOSTNAME or 'https://localhost:8080')
# ))
# class ProjectGPUAPI(generics.mixins.ListModelMixin,APIView):
#     parser_classes = (JSONParser, FormParser, MultiPartParser)
#     queryset = ProjectGPU.objects.all()
#     permission_classes = (IsAuthenticated,)
#     serializer_class = UserSerializer
#     def get_queryset(self):
#         return ProjectGPU.objects.filter()

#     def filter_queryset(self, queryset):
#         return ProjectGPU.objects.all()

#     def get(self, request, *args, **kwargs):
#         return Response(
#             list(ProjectGPU.objects.values('id', 'project_id', 'host', 'port','api_key','api_secret','name','gpu_desc','status'))
#         )

#     def post(self, request, *args, **kwargs):
#         j_obj = json.loads(request.body)
#         # print(j_obj )
#         user = request.user
#         if int(j_obj["id"]) > 0:
#             item =ProjectGPU.objects.filter(id=int(j_obj["id"])).first()
#             item.project_id=j_obj["project_id"]
#             item.status=j_obj["status"]
#             item.host=j_obj["host"]
#             item.port=j_obj["port"]
#             item.api_key=j_obj["api_key"]
#             item.api_secret=j_obj["api_secret"]
#             item.name=j_obj["name"]
#             item.gpu_desc=j_obj["gpu_desc"]
#             item.save()
#         else:
#             ProjectGPU.objects.create(
#                     user_id=user.id,
#                     project_id=j_obj["project_id"],
#                     status=j_obj["status"],
#                     host=j_obj["host"],
#                     port=j_obj["port"],
#                     api_key=j_obj["api_key"],
#                     api_secret=j_obj["api_secret"],
#                     name=j_obj["name"],
#                     gpu_desc=j_obj["gpu_desc"]
#                 )
#         # print(result )
#         return Response({"msg":"done"}, status=200)
# @method_decorator(name='get', decorator=swagger_auto_schema(
#         tags=['Project Checkpoint'],
#         operation_summary='Retrieve Checkpoint',
#         operation_description=''
#     ))
# @method_decorator(name="post", decorator=swagger_auto_schema(
#     tags=['Project Checkpoint'],
#     operation_summary='Recalculate stats for this project',
#     operation_description="""
#     ```bash
#     curl -X POST {}/api/projects/<int:pk>/checkpoint/ -H 'Authorization: Token abc123'
#     ```
#     """.format(settings.HOSTNAME or 'https://localhost:8080')
# ))
# class ProjectCheckpointAPI(generics.mixins.ListModelMixin,APIView):
#     parser_classes = (JSONParser, FormParser, MultiPartParser)
#     queryset = ProjectCheckpoint.objects.all()
#     permission_classes = (IsAuthenticated,)
#     serializer_class = UserSerializer
#     def get_queryset(self):
#         return ProjectCheckpoint.objects.filter()

#     def filter_queryset(self, queryset):
#         return ProjectCheckpoint.objects.all()

#     def get(self, request, *args, **kwargs):
#         return Response(
#             list(ProjectCheckpoint.objects.values('id', 'project_id', 's3_url', 'train_created_at','dataset_id','status'))
#         )

#     def post(self, request, *args, **kwargs):
#         j_obj = json.loads(request.body)
#         # print(j_obj )
#         user = request.user
#         if int(j_obj["id"]) > 0:
#             item =ProjectCheckpoint.objects.filter(id=int(j_obj["id"])).first()
#             item.project_id=j_obj["project_id"]
#             item.status=j_obj["status"]
#             item.s3_url=j_obj["s3_url"]
#             item.train_created_at=j_obj["train_created_at"]
#             item.dataset_id=j_obj["dataset_id"]
#             item.save()
#         else:
#             ProjectCrawlQueue.objects.create(
#                     user_id=user.id,
#                     project_id=j_obj["project_id"],
#                     status=j_obj["status"],
#                     s3_url=j_obj["s3_url"],
#                     train_created_at=j_obj["train_created_at"],
#                     dataset_id=j_obj["dataset_id"]
#                 )
#         # print(result )
#         return Response({"msg":"done"}, status=200)


@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=['Projects'],
        operation_summary='Get info gpu, tflop, param',
        operation_description="Get info gpu, tflop, param",
        manual_parameters=[
            openapi.Parameter(
                name='project_id',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description='project id',
                required=False
            ),
            openapi.Parameter(
                name='model_id',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description='model id',
                required=False
            ),
            openapi.Parameter(
                name='paramaster',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description='paramaster',
                required=True
            ),
            openapi.Parameter(
                name='compute_id',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description='compute id',
                required=False
            ),
            openapi.Parameter(
                name='gpu_list_id',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                description='List of GPU List IDs',
                required=True
            ),
            openapi.Parameter(
                name='image_width',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description='image_width',
                required=False
            ),
            openapi.Parameter(
                name='image_height',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description='image_height',
                required=False
            ),
            openapi.Parameter(
                name='token',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description='token',
                required=False
            ),
            openapi.Parameter(
                name='catalog_id',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description='token',
                required=False
            ),
        ]
    ),
)

class ComputeGPUAPI(generics.ListAPIView):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        project_id = self.request.query_params.get('project_id')
        model_id = self.request.query_params.get('model_id')
        compute_id = self.request.query_params.get('compute_id')
        gpu_list_id = self.request.query_params.get('gpu_list_id')
        paramaster = self.request.query_params.get('paramaster')
        accuracy = self.request.query_params.get('accuracy')
        epochs = self.request.query_params.get('epochs')
        gpu_list_id = gpu_list_id.split(',') 
        # Assuming you have instances of Project and ComputeGPU
        project_instance =None
        if project_id and project_id != '0': 
            project_instance = Project.objects.filter(pk=project_id).first()
            data_type_prj = project_instance.data_types
        model_instance = ModelMarketplace.objects.filter(pk=model_id).first()
        # group_model = AnnotationTemplate.objects.filter(catalog_model_id=model_instance.catalog_id).first()
        compute_instance = ComputeMarketplace.objects.filter(pk=compute_id).first()
        # framework =json.loads(model_instance.config)["framework"]
        
        # Calculate total TFLOPS, GPU memory, and set efficiency
        total_tflops = 0
        total_gpu_memory = 0
        total_power_consumption = 0
        total_price_per_hour = 0
        for gpu_id in gpu_list_id:
            gpu = ComputeGPU.objects.filter(pk=gpu_id).first()
            gpu_price = ComputeGpuPrice.objects.filter(compute_gpu_id=gpu_id).first()

            if gpu:
                # Calculate TFLOPS from GPU name
                # tflops = map_gpu_to_tflops(gpu.gpu_name)
                if gpu.gpu_tflops:
                    tflops = float(gpu.gpu_tflops)
                else:
                    tflops = 1
                
                total_tflops += tflops if tflops else 0

                # Calculate power consumption from GPU name
                power_consumption = map_gpu_to_power_consumption(gpu.gpu_name)
                total_power_consumption += power_consumption if power_consumption else 0

                if gpu_price:
                    total_price_per_hour += gpu_price.price
                
                # Calculate total GPU memory
                if gpu.gpu_memory is not None and gpu.gpu_memory != "" :
                    gpu_memory = int(gpu.gpu_memory) #convert_memory_to_byte(gpu.gpu_memory)
                    total_gpu_memory += gpu_memory
                    # save gpu convert to number
                    gpu.gpu_memory = gpu_memory
                    gpu.save()
        
        # # Define the models
        hours = 1
        param_value = 0
        total_flops = 0
        total_cost = 0
        can_rent = True
        macs = '0'
        num_gpu =len(gpu_list_id)
        cv_model_type = ['Computer Vision']
        nlp_llm_model_type = ['Generative AI', 'Natural Language Processing', 'Ranking & Scoring', 'Time Series Analysis', 'Large Language Model']
        try:
            acc = 0.7
            if accuracy:
                acc = float(accuracy)/100

            epochs = 1
            if epochs:
                epoch = epochs
                
            if paramaster:
                if paramaster == 'check':
                    hours, total_flops, param_value = calc_param_from_tflop(total_tflops, acc, epoch)
                else:
                    hours, total_flops, param_value = calc_tflop_from_param(total_tflops, paramaster, acc, epoch)
            # if framework == "pytorch":
            #     if group_model.group in cv_model_type:
            #         token_length = json.loads(model_instance.config)["token_length"]
            #         args_mem = config_cacl_mem().parse_args(["--num-gpus", f"{num_gpu}", "--num-layers", "44", "--sequence-length", f"{token_length}", "--num-attention-heads", "64", "--hidden-size", "6144", "--batch-size-per-gpu", "1", "--checkpoint-activations", "--zero-stage", "1", "--partition-activations", "--pipeline-parallel-size", "1", "--tensor-parallel-size", "1"])
            #         total_params, single_replica_mem_gib = calc_mem(args_mem)

            #         args = config_parser().parse_args(["-l", "12", "-hs", "768", "--moe", "-e", "512"])
            #         total_flops, hours = calc_time_neeed_nlp(args, num_gpu, total_params)

            #         if single_replica_mem_gib > total_gpu_memory: 
            #             can_rent = False

            #     elif group_model.group in nlp_llm_model_type:
            #         vit = timm.create_model('vit_base_patch16_224').to(device='cuda:0') 
            #         input_shape = (project_instance.batch_size, 3, project_instance.image_height, project_instance.image_width)
            #         x = torch.randn([project_instance.batch_size, 3, project_instance.image_height, project_instance.image_width]).to(device='cuda:0')
            #         single_replica_mem_gib = calc_mem_pytorch_images(vit, x, input_shape)
            #         hours, total_flops, param_value = calc_time_neeed_pytorch_images(vit, input_shape, num_gpu)
                    
            #         if single_replica_mem_gib > total_gpu_memory: 
            #             can_rent = False

            # elif framework == "tensowflow":
            # if group_model.group in cv_model_type:
            #     token_length = json.loads(model_instance.config)["token_length"]
            #     args_mem = config_cacl_mem().parse_args(["--num-gpus", f"{num_gpu}", "--num-layers", "44", "--sequence-length", f"{token_length}", "--num-attention-heads", "64", "--hidden-size", "6144", "--batch-size-per-gpu", "1", "--checkpoint-activations", "--zero-stage", "1", "--partition-activations", "--pipeline-parallel-size", "1", "--tensor-parallel-size", "1"])
            #     total_params, single_replica_mem_gib = calc_mem(args_mem)
            #     args = config_parser().parse_args(["-l", "12", "-hs", "768", "--moe", "-e", "512"])
            #     total_flops, hours = calc_time_neeed_nlp(args, num_gpu, total_params)


                # if single_replica_mem_gib > total_gpu_memory: 
                #     can_rent = False
                
            # elif group_model.group in nlp_llm_model_type:
            # else:

            # if "image" in data_type_prj: 
            #     from tensorflow.keras.applications import EfficientNetB3
            #     import tensorflow as tf

            #     model = tf.keras.applications.Xception(
            #         weights='imagenet',
            #         input_shape=(150, 150, 3),
            #         include_top=False
            #     ) 
            #     param_value = model.count_params()
            #     total_flops, hours = calc_mem_tf(model, project_instance.batch_size, num_gpu)
            #     single_replica_mem_gib = calc_mem_gpu_tf(model, project_instance.batch_size)
                
            #     if single_replica_mem_gib > total_gpu_memory: 
            #         can_rent = False
            # elif "text" in data_type_prj or 'llm' in data_type_prj or  'nlp' in data_type_prj:
            #     token_length =  self.request.query_params.get('token') # json.loads(model_instance.config)["token_length"]
            #     args_mem = config_cacl_mem().parse_args(["--num-gpus", f"{num_gpu}", "--num-layers", "44", "--sequence-length", f"{token_length}", "--num-attention-heads", "64", "--hidden-size", "6144", "--batch-size-per-gpu", "1", "--checkpoint-activations", "--zero-stage", "1", "--partition-activations", "--pipeline-parallel-size", "1", "--tensor-parallel-size", "1"])
            #     total_params, single_replica_mem_gib = calc_mem(args_mem)
            #     args = config_parser().parse_args(["-l", "12", "-hs", "768", "--moe", "-e", "512"])
            #     total_flops, hours = calc_time_neeed_nlp(args, num_gpu, total_params)


            #     if single_replica_mem_gib > total_gpu_memory: 
            #         can_rent = False
            
            if hours > 1:
                total_cost = total_price_per_hour*hours
            else:
                total_cost = total_price_per_hour

            if total_flops == 0:
                total_gpu_memory = 0

            if not total_flops or total_flops == 0:
                can_rent = False
            
            if total_tflops*10**12 < total_flops:
                can_rent = False

        except Exception as e:
            can_rent = False
            print(e)

        token_symbol = 'usd'
        response_data = {
            "paramasters": int(param_value),
            "mac": f"{total_flops/2}",
            "gpu_memory": total_gpu_memory,
            "tflops": total_flops,
            "time": hours,
            "total_cost": f"{total_cost}",
            "total_power_consumption": total_power_consumption,
            "can_rent": can_rent,
            "token_symbol": token_symbol,
        }

        return response_data

    def get(self, request, *args, **kwargs):
        response_data = self.get_queryset()
        return Response(response_data, status=status.HTTP_200_OK)

@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Projects Docker'],
    operation_summary='Reset endpoint cluster ML',
    operation_description="Reset endpoint cluster ML",
    manual_parameters=[
        openapi.Parameter('project_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="ID of the project")
    ]
))

class ResetMLPortAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # print(self.request.query_params)
        # print(kwargs)
        from projects.models import Project
        from core.permissions import permission_org

        project = Project.objects.filter(id=int(float(self.request.query_params.get('project_id')))).first()
        project_id = self.request.query_params.get('project_id')

        if not permission_org(self.request.user, project):
            return Response("You do not have permission to perform this action.", status=status.HTTP_403_FORBIDDEN)
        
        ml_backend = MLBackend.objects.filter(
            project=project_id,
            deleted_at__isnull=True
        ).order_by('-id')
        # import re
        if len(ml_backend)>0 :
            ml = ml_backend.first()
            parsed = urlparse(ml.url)
            ml_address = parsed.hostname
            ml_port = parsed.port

            # ip = re.findall( r'([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{2,4})?',ml.url )
            # ml_gpu = MLGPU.objects.filter(ml_id=ml.id).first()
            # if ml_gpu:
            #     _compute = ComputeMarketplace.objects.filter(
            #             author_id=self.request.user.id,
            #             id=ml_gpu.compute_id,
            #         ).first()
              
            #     if _compute:
            try:
                # nginx_proxy_manager = NginxReverseProxy(f'{settings.REVERSE_ADDRESS}', f'{_compute.ip_address}_{_compute.port}')
                nginx_proxy_manager = NginxReverseProxy(f'{settings.REVERSE_ADDRESS}', f'{ml_address}_{ml_port}')
                nginx_proxy_manager.remove_nginx_service()
                        # nginx_proxy_manager = NginxReverseProxyManager(f'{settings.REVERSE_ADDRESS}', project_id, _compute.ip_address)
                        
                        # nginx_proxy_manager.remove_nginx_service()

                        # client = docker.DockerClient(base_url=f'{settings.REVERSE_ADDRESS}')
                        # containers = client.containers.list(filters={'name': f"project-{project_id}_*"}, all=True)
                        
                        # if len(containers) == 0:
                        #     raise RestValidationError('No container found for this project')
                        
                        # proxy_port = nginx_proxy_manager.configure_reverse_proxy(containers)
                        
                # proxy_url = f"https://{_compute.ip_address}:{_compute.port}"
                if "https" in ml.url:
                    proxy_url = "https://"+convert_url(ml.url, True)
                else:
                    proxy_url = "http://"+convert_url(ml.url, False)

                parsed_url = urlparse(proxy_url)
                host = parsed_url.hostname
                port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)

                ProjectMLPort.objects.create(project_id = project_id, port = port, host = host)
                
                return Response({ "proxy_url": proxy_url }, status=status.HTTP_200_OK)
            
            except ProjectMLPort.DoesNotExist:
                return Response({'error': 'ProjectMLPort not found'}, status=status.HTTP_404_NOT_FOUND)
        # else:
        #         return Response({'error': 'ProjectMLPort not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
                return Response({'error': 'ProjectMLPort not found'}, status=status.HTTP_404_NOT_FOUND)

@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Projects Docker'],
    operation_summary='Get endpoint cluster ML',
    operation_description="Get endpoint cluster ML",
    manual_parameters=[
        openapi.Parameter('project_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="ID of the project"),
        openapi.Parameter('network_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="ID of the network")
    ]
))

class GetMLPortAPIView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            project_id = self.request.query_params.get('project_id')
            network_id = self.request.query_params.get('network_id')
            # checkpoint_id = self.request.query_params.get('checkpoint_id')
            proxy_url = ""

            # if checkpoint_id:
            #     checkpoint_instance = CheckpointModelMarketplace.objects.filter(project_id=project_id, id=checkpoint_id).first()
            #     ml_backend = MLBackend.objects.filter(project_id=project_id, id=checkpoint_instance.ml_id).first()
            #     proxy_url = ml_backend.url
            #     return Response({ "proxy_url": proxy_url }, status=status.HTTP_200_OK)
            
            proxy_project = ProjectMLPort.objects.filter(project_id = project_id, network_id =network_id ).first()
            ml = MLBackend.objects.filter(project_id=project_id, deleted_at__isnull=True).filter(
                Q(
                    id__in=MLNetworkHistory.objects.filter(
                        ml_network__id=network_id,
                        ml_id=OuterRef("id"),
                        deleted_at__isnull=True,
                    ).order_by("-id").values("ml_id")
                )
            ).first()
            try:
                if ml.install_status == "installing":
                    return Response({ "proxy_url": "" }, status=status.HTTP_200_OK)
                
                ml_gpu = MLGPU.objects.filter(ml_id=ml.id, deleted_at__isnull=True).first()
                model_instance = ModelMarketplace.objects.filter(id=ml_gpu.model_id).first()
                schema = "http"
                if model_instance and model_instance.schema:
                    schema = f'{model_instance.schema}'.replace('://', '')

                if "grpc" not in schema:
                    if proxy_project:
                        host_proxy = proxy_project.host
                        port_proxy = proxy_project.port
                        if schema == 'https':
                            proxy_url = f"https://{host_proxy}:{port_proxy}"
                            proxy_url = "https://"+convert_url(proxy_url, True)
                        else:
                            proxy_url = f"http://{host_proxy}:{port_proxy}"
                            proxy_url = "https://"+convert_url(proxy_url, False)

                    else:
                        proxy_url = ml.url
                        if "https" in proxy_url:
                            proxy_url = "https://"+convert_url(proxy_url, True)
                        else:
                            proxy_url = "https://"+convert_url(proxy_url, False)
                else:
                    if proxy_project:
                        host_proxy = proxy_project.host
                        port_proxy = proxy_project.port
                        proxy_url = f"grpc://{host_proxy}:{port_proxy}" 
                    else:
                        proxy_url = ml.url

            except Exception as e:
                project = Project.objects.filter(id = project_id)
                try: 
                    host_template = project.template.ml_ip
                    port_template = project.template.ml_port
                    proxy_url = f"http://{host_template}:{port_template}"
                    proxy_url = "https://"+convert_url(proxy_url, True)
                except:
                    proxy_url = ""
            
            return Response({ "proxy_url": proxy_url }, status=status.HTTP_200_OK)
        
        except ProjectMLPort.DoesNotExist:
            return Response({'error': 'ProjectMLPort not found'}, status=status.HTTP_404_NOT_FOUND)

@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Project'],
    operation_summary='Auto project api',
))
class AutoAPI(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        from ml.api_connector import MLApi
        from tasks.models import Task
        from projects.models import Project
        api = MLApi(url = 'http://69.197.168.145:8018/')
        tasks = Task.objects.filter(project_id=8)
        project = Project.objects.filter(id=8).first()
        for task in tasks:
            from tasks.serializers import TaskSimpleSerializer, PredictionSerializer
            tasks_ser = TaskSimpleSerializer(tasks, many=True).data

        return Response(tasks_ser, status=status.HTTP_201_CREATED)

@method_decorator(name='post', decorator=swagger_auto_schema(
        tags=['Import'],
        operation_summary='Upload dataset',
        operation_description='Upload dataset',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'project_id':openapi.Schema(type=openapi.TYPE_STRING, description='project_id'),
                'keyword':openapi.Schema(type=openapi.TYPE_STRING, description='keyword'),
                'type':openapi.Schema(type=openapi.TYPE_STRING, description='type'),
                'quantity':openapi.Schema(type=openapi.TYPE_STRING, description='quantity'),
                'search_id':openapi.Schema(type=openapi.TYPE_STRING, description='search_id'),
                'searchAll':openapi.Schema(type=openapi.TYPE_STRING, description='searchAll')
            },
            required=['project_id']
        )
    ))

class CrawlHistoryAPI(generics.ListAPIView):
    
    def post(self, request, *args, **kwargs):
        try:
            project_id = self.request.data.get("project_id")
            keyword = self.request.data.get("keyword")
            type = self.request.data.get("type")
            quantity = self.request.data.get("quantity")
            search_id = self.request.data.get("search_id")
            searchAll = self.request.data.get("searchAll")
            project_id = self.request.data.get("project_id")
            if searchAll=='true':
                CrawlHistory.objects.filter(project_id=project_id).update(deleted_at=timezone.now())
                return Response({"message": "Done"}, status=200)
            crawl_history = CrawlHistory.objects.filter(project_id=project_id, keyword=keyword, type=type, quantity=quantity, deleted_at__isnull=True)
            if crawl_history:
                search_id = crawl_history.first().search_id
                return Response({"search_id": search_id}, status=200)
            else:
                CrawlHistory.objects.filter(project_id=project_id).update(deleted_at=timezone.now())
                if search_id:
                    CrawlHistory.objects.create(project_id=project_id, keyword=keyword, type=type, quantity=quantity, search_id=search_id)
                return Response({"message": search_id}, status=200)
            
        except Exception as e:
            return Response({"message": "There are nothing"}, status=500)


class ProjectLabelAPI(generics.CreateAPIView, generics.DestroyAPIView):
    permission_required = all_permissions.projects_change

    def post(self, request, *args, **kwargs):
        project_id = request.data.get("pk")
        label_type = request.data.get("type")
        name = request.data.get("name")
        labels = request.data.get("labels")
        color = request.data.get("color")
        project_label = ProjectLabels(project_id)
        result = project_label.add_label(label_type, name, labels, color)

        if result is None:
            return Response({"message": "Failed to add new label"}, status=400)
        else:
            return Response({"message": "New label has been added", "label_config": result})

    def delete(self, request, *args, **kwargs):
        project_id = request.data.get("pk")
        label_type = request.data.get("type")
        name = request.data.get("name")
        labels = request.data.get("labels")
        project_label = ProjectLabels(project_id)
        result = project_label.remove_label(label_type, name, labels)

        if result is None:
            return Response({"message": "Failed to remove label"}, status=400)
        else:
            return Response({"message": "Label has been removed", "label_config": result})

@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Reverse URL'],
    operation_summary='Reverse url',
    operation_description="Reverse url",
    request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'url':openapi.Schema(type=openapi.TYPE_STRING, description='url')
            })
))

class ReverseURLAPI(APIView):
    def post(self, request, *args, **kwargs):
        url = request.data.get("url")
        if "https" in url:
            proxy_url = "https://"+convert_url(url, True)
        else:
            proxy_url = "https://"+convert_url(url)

        return Response({ "proxy_url": proxy_url }, status=status.HTTP_200_OK)

@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Set ENV'],
    operation_summary='Set ENV',
    operation_description="Set ENV",
    request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'env':openapi.Schema(type=openapi.TYPE_STRING, description='env'),
                'value':openapi.Schema(type=openapi.TYPE_STRING, description='value')
            })
))

class SetEnvAPI(APIView):
    def post(self, request, *args, **kwargs):
        env = request.data.get("env")
        value = request.data.get("value")

        os.environ[env] = value

        return Response(status=status.HTTP_200_OK)


@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Redact PII Entity'],
    operation_summary='Add entity',
    request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'pk': openapi.Schema(type=openapi.TYPE_INTEGER, description='project ID'),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='redactor name'),
                'entity': openapi.Schema(type=openapi.TYPE_STRING, description='new entity'),
            })
))
@method_decorator(name='delete', decorator=swagger_auto_schema(
    tags=['Redact PII Entity'],
    operation_summary='Remove entity',
    request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'pk': openapi.Schema(type=openapi.TYPE_INTEGER, description='project ID'),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='redactor name'),
                'entity': openapi.Schema(type=openapi.TYPE_STRING, description='to be removed entity'),
            })
))
class ProjectPiiAPI(generics.CreateAPIView, generics.DestroyAPIView):
    permission_required = all_permissions.projects_change

    def post(self, request, *args, **kwargs):
        project_id = request.data.get("pk")
        name = request.data.get("name")
        entity = request.data.get("entity")
        project_label = ProjectPiiEntities(project_id)
        result = project_label.add(name, entity)

        if result is None:
            return Response({"message": "Failed to add new PII entity"}, status=400)
        else:
            return Response({"message": "New PII entity has been added", "label_config": result})

    def delete(self, request, *args, **kwargs):
        project_id = request.data.get("pk")
        name = request.data.get("name")
        entity = request.data.get("entity")
        project_label = ProjectPiiEntities(project_id)
        result = project_label.remove(name, entity)

        if result is None:
            return Response({"message": "Failed to remove PII entity"}, status=400)
        else:
            return Response({"message": "PII entity has been removed", "label_config": result})
