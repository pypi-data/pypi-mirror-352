"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import json
import logging
import drf_yasg.openapi as openapi
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
from django.conf import settings

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import OuterRef, Subquery, Q

from core.feature_flags import flag_set
from core.permissions import all_permissions, ViewClassPermission
from core.utils.common import get_object_with_check_and_log
from core.utils.paginate import SetPagination
from django.db.models import Max
from ml.models import (
    MLBackendTrainJob,
    MLBackend,
    MLGPU,
    MLBackendStatus,
    MLBackendState,
    MLNetwork,
    MLNetworkHistory,
)
from users.serializers import UserSerializer
from projects.models import Project, Task, ProjectMLPort
from ml.serializers import (
    MLBackendSerializer,
    MLInteractiveAnnotatingRequest,
    MLBackendAdminViewSerializer,
    MLBackendTrainJobAdminViewSerializer,
    MLBackendStatusSerializer,
    MLUpdateConfigSerializer,
    MLNetworkSerializer,
    MLNetworkHistorySerializer,
    HistoryDeploySerializer
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from core.utils.docker_container_action import dockerContainerStartStop
from urllib.parse import urlparse
from compute_marketplace.models import ComputeMarketplace, ComputeGPU
from core.utils.docker_container_create import createDocker
from projects.serializers import ProjectMLPortSerializer
from django.utils import timezone
from ml.functions import check_connect_ml_vast
from .functions import destroy_ml_instance
from compute_marketplace.vastai_func import vast_service
from compute_marketplace.plugin_provider import vast_provider
from django.shortcuts import get_object_or_404
from model_marketplace.models import ModelMarketplace, History_Build_And_Deploy_Model, History_Rent_Model
from core.permissions import permission_org
logger = logging.getLogger(__name__)


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["Machine Learning"],
        operation_summary="Add ML Backend",
        operation_description="""
    Add an ML backend to a project using the AiXBlock UI or by sending a POST request using the following cURL 
    command:
    ```bash
    curl -X POST -H 'Content-type: application/json' {host}/api/ml -H 'Authorization: Token abc123'\\
    --data '{{"url": "http://localhost:9090", "project": {{project_id}}}}' 
    """.format(
            host=(settings.HOSTNAME or "https://localhost:8080")
        ),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "project": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="Project ID"
                ),
                "url": openapi.Schema(
                    type=openapi.TYPE_STRING, description="ML backend URL"
                ),
            },
        ),
    ),
)
@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["Machine Learning"],
        operation_summary="List ML backends",
        operation_description="""
    List all configured ML backends for a specific project by ID.
    Use the following cURL command:
    ```bash
    curl {host}/api/ml?project={{project_id}} -H 'Authorization: Token abc123'
    """.format(
            host=(settings.HOSTNAME or "https://localhost:8080")
        ),
        manual_parameters=[
            openapi.Parameter(
                name="project",
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_QUERY,
                description="Project ID",
            ),
            openapi.Parameter(
                name="ml_network",
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_QUERY,
                description="ml network ID",
            ),
        ],
    ),
)
class MLBackendListAPI(generics.ListCreateAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_required = ViewClassPermission(
        GET=all_permissions.projects_view,
        POST=all_permissions.projects_change,
    )
    serializer_class = MLBackendSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_interactive"] 

    def get_queryset(self):
        project_pk = self.request.query_params.get('project')
        ml_network_id = self.request.query_params.get('ml_network')
        is_deploy = self.request.query_params.get('is_deploy', None)

        if is_deploy=="true":
            is_deploy = True
        else:
            is_deploy = False

        project = get_object_with_check_and_log(self.request, Project, pk=project_pk)
        self.check_object_permissions(self.request, project)

        # Get MLBackend entries related to the project
        if ml_network_id:
            ml_backends = MLBackend.objects.filter(
                project_id=project.id,
                deleted_at__isnull=True,
                mlnetwork_id = ml_network_id,
                # is_deploy = is_deploy
            )
            
            if ml_backends and is_deploy:
                ml_backends = ml_backends.filter(id=ml_backends.order_by("-id").first().id).all()
            elif not ml_backends:
                ml_backends = MLBackend.objects.filter(
                    project_id=project.id,
                    deleted_at__isnull=True,
                    is_deploy = False
                ).order_by("-id").all()
            else:
                ml_backends = ml_backends.order_by("-id").all()
        else:
            ml_backends = MLBackend.objects.filter(
                project_id=project.id,
                deleted_at__isnull=True,
                is_deploy = is_deploy
            )

            if ml_backends and is_deploy:
                ml_backends = ml_backends.filter(id=ml_backends.order_by("-id").first().id).all()
            elif not ml_backends:
                ml_backends = MLBackend.objects.filter(
                    project_id=project.id,
                    deleted_at__isnull=True,
                    # is_deploy = False
                ).order_by("-id").all()
            else:
                ml_backends = ml_backends.order_by("-id").all()

        for mlb in ml_backends:
            compute_id = None
            mlgpu = MLGPU.objects.filter(ml_id=mlb.id, deleted_at__isnull=True).first()
            if mlgpu:
                compute_id = mlgpu.compute_id
            if mlb.install_status != "installing":
                mlb.update_state(compute_id)

            if mlb.state in ["DI", "ER"]:
                MLBackendStatus.objects.filter(ml_id=mlb.id, project_id=project_pk).update(status="worker", status_training="join_master")
                if is_deploy:
                    ml_backends = []

        if ml_network_id:
            # Get MLNetwork related to the project
            ml_network = MLNetwork.objects.filter(id=ml_network_id, deleted_at__isnull=True).first()
            
            if ml_network:
                # Get MLNetworkHistory entries related to the MLNetwork
                ml_network_histories = MLNetworkHistory.objects.filter(
                    ml_network_id=ml_network.id, deleted_at__isnull=True
                ).values_list('ml_id', flat=True)

                # Filter ml_backends further based on ml_network_histories
                filtered_ml_backends = ml_backends.filter(
                    id__in=ml_network_histories
                )
                
                return filtered_ml_backends
        
        return ml_backends
    def perform_create(self, serializer):
        ml_backend =serializer.save()
        ml_backend.update_state()

    def get(self, request, *args, **kwargs):
        try:
            return super(MLBackendListAPI, self).get(request, *args, **kwargs)
        except Exception as e: 
            print(e)
            return Response([], status=200)

    def post(self, request, *args, **kwargs):
        return super(MLBackendListAPI, self).post(request, *args, **kwargs)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["Machine Learning"],
        operation_summary="List ML backends Monitor",
        operation_description="""
    List all configured ML backends for a specific project by ID.
    Use the following cURL command:
    ```bash
    curl {host}/api/ml?project={{project_id}} -H 'Authorization: Token abc123'
    """.format(
            host=(settings.HOSTNAME or "https://localhost:8080")
        ),
        manual_parameters=[
            openapi.Parameter(
                name="project",
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_QUERY,
                description="Project ID",
            ),
            openapi.Parameter(
                name="ml_network",
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_QUERY,
                description="ml network ID",
            ),
        ],
    ),
)
class MLBackendListMonitorAPI(generics.ListAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_required = ViewClassPermission(
        GET=all_permissions.projects_view,
        POST=all_permissions.projects_change,
    )
    serializer_class = MLBackendSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_interactive"] 

    def get_queryset(self):
        project_pk = self.request.query_params.get('project')
        ml_network_id = self.request.query_params.get('ml_network')
        project = get_object_with_check_and_log(self.request, Project, pk=project_pk)
        self.check_object_permissions(self.request, project)

        # Get MLBackend entries related to the project
        ml_backends = MLBackend.objects.filter(
            project_id=project.id,
            deleted_at__isnull=True
        ).order_by("id").all()

        for mlb in ml_backends:
            compute_id = None
            mlgpu = MLGPU.objects.filter(ml_id=mlb.id, deleted_at__isnull=True).first()
            if mlgpu:
                compute_id = mlgpu.compute_id
            if mlb.install_status != "installing":
                mlb.update_state(compute_id)

            if mlb.state in ["DI", "ER"]:
                MLBackendStatus.objects.filter(ml_id=mlb.id, project_id=project_pk).update(status="worker", status_training="join_master")

        if ml_network_id:
            # Get MLNetwork related to the project
            ml_network = MLNetwork.objects.filter(id=ml_network_id, deleted_at__isnull=True).first()

            if ml_network:
                # Get MLNetworkHistory entries related to the MLNetwork
                ml_network_histories = MLNetworkHistory.objects.filter(
                    ml_network_id=ml_network.id, deleted_at__isnull=True
                ).values_list('ml_id', flat=True)

                # Filter ml_backends further based on ml_network_histories
                filtered_ml_backends = ml_backends.filter(
                    id__in=ml_network_histories
                )

                return filtered_ml_backends

        return ml_backends

    def get(self, request, *args, **kwargs):
        try:
            return super(MLBackendListAPI, self).get(request, *args, **kwargs)
        except Exception as e: 
            print(e)
            return Response([], status=200)


@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=['Machine Learning Docker'],
        operation_summary='Stop or Start Docker ML',
        operation_description="""
    Stop or Start Docker ML
    Use the following cURL command:
    ```bash
    curl {host}/api/ml/docker?ml_id={{ml_id}}&action={{action}} -H 'Authorization: Token abc123'
    """.format(
            host=(settings.HOSTNAME or 'https://localhost:8080')
        ),
        manual_parameters=[
            openapi.Parameter(
                name='ml_id',
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_QUERY,
                description='ML ID'),
            openapi.Parameter(
                name='action',
                type=openapi.TYPE_STRING,
                in_=openapi.IN_QUERY,
                description='Action docker: start | stop'),
        ],
    ))
class MLBackendDockerAPI(generics.RetrieveAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_required = ViewClassPermission(
        GET=all_permissions.projects_view,
        POST=all_permissions.projects_change,
    )
    serializer_class = MLBackendSerializer

    def perform_create(self, serializer):
        ml_backend = serializer.save()
        ml_backend.update_state()

    def get(self, request, *args, **kwargs):
        ml_pk = self.request.query_params.get('ml_id')
        action = self.request.query_params.get('action')
        print("action", action)
        ml_backends = MLBackend.objects.filter(id=ml_pk).first()

        if not permission_org(self.request.user, ml_backends.project):
            return Response("You do not have permission to perform this action.", status=status.HTTP_403_FORBIDDEN)
        
        parsed_url = urlparse(ml_backends.url)
        ip_address = parsed_url.hostname
        ml_gpu = MLGPU.objects.filter(ml_id=ml_pk).first()
        compute = ComputeMarketplace.objects.filter(id=ml_gpu.compute_id).first()
        print(ml_gpu)
        if ml_gpu is None:
            return Response('Not found ML GPU', status=404)  # Use return to return the Response

        model = ModelMarketplace.objects.filter(id=ml_gpu.model_id).first()
        if model is None:
            return Response("Not found Model", status=404)

        _port = '0'
        if action == 'delete' and compute.type != "MODEL-PROVIDER-VAST":
            _port= dockerContainerStartStop(base_image= model.docker_image, action=action, ip_address=ip_address,project_id=ml_backends.project.id, model_id=model.pk )

        if compute.type == "MODEL-PROVIDER-VAST":
            _port = compute.port

        ml_backend_status = MLBackendStatus.objects.filter(ml_id = ml_pk, project_id = ml_backends.project_id, deleted_at__isnull=True).first()
        if action == 'start' and compute.type == "MODEL-PROVIDER-VAST":
            try:
                # vast_service.stop_start_instance(compute.infrastructure_id, "start")
                vast_provider.start_compute(compute.infrastructure_id)
                ml_backends.state = MLBackendState.CONNECTED
                ml_backends.save()
            except Exception as e:
                print(f"An error occurred while trying to {action} the instance: {e}")
        if action == "stop" and compute.type == "MODEL-PROVIDER-VAST":
            try:
                # vast_service.stop_start_instance(compute.infrastructure_id, "stop")
                vast_provider.stop_compute(compute.infrastructure_id)
                ml_backends.state = MLBackendState.DISCONNECTED
                ml_backends.save()
                import time
                time.sleep(5)
            except Exception as e:
                print(f"An error occurred while trying to {action} the instance: {e}")
        if action == "stop" and compute.type != "MODEL-PROVIDER-VAST":
            try:
                _port = dockerContainerStartStop(
                    base_image=model.docker_image,
                    action=action,
                    ip_address=ip_address,
                    project_id=ml_backends.project.id,
                    model_id=model.pk,
                )
                ml_backends.state = MLBackendState.DISCONNECTED
                ml_backends.save()
                import time

                time.sleep(5)
            except Exception as e:
                print(f"An error occurred while trying to {action} the instance: {e}")

        if action == 'start' and _port != '0':
            ml_gpu.port = _port
            model.port =_port
            model.save()
            ml_backends.url = "https://"+ model.ip_address +':'+_port
            ml_backends.save()
            ml_gpu.save()

        # if action == 'stop':
        #     from rest_framework.authtoken.models import Token
        #     token = Token.objects.filter(user=self.request.user)
        #     ml_backends.stop_train(token.first().key)

        if ml_backend_status:
            if ml_backend_status.status == "master":
                MLBackendStatus.objects.filter(project_id = ml_backends.project_id, deleted_at__isnull=True).update(status = "worker", status_training = "join_master")
            else:
                ml_backend_status.status = "worker"
                ml_backend_status.status_training = "join_master"
                ml_backend_status.type_training = "manual"
                ml_backend_status.save()

        serializer = MLBackendStatusSerializer(ml_backend_status)

        try:
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response("An error occurred", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(
    name='patch',
    decorator=swagger_auto_schema(
        tags=['Machine Learning'],
        operation_summary='Update ML Backend',
        operation_description="""
    Update ML backend parameters using the AiXBlock UI or by sending a PATCH request using the following cURL command:
    ```bash
    curl -X PATCH -H 'Content-type: application/json' {host}/api/ml/{{ml_backend_ID}} -H 'Authorization: Token abc123'\\
    --data '{{"url": "http://localhost:9091"}}' 
    """.format(
            host=(settings.HOSTNAME or 'https://localhost:8080')
        ),
    ),
)
@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=['Machine Learning'],
        operation_summary='Get ML Backend',
        operation_description="""
    Get details about a specific ML backend connection by ID. For example, make a GET request using the
    following cURL command:
    ```bash
    curl {host}/api/ml/{{ml_backend_ID}} -H 'Authorization: Token abc123'
    """.format(
            host=(settings.HOSTNAME or 'https://localhost:8080')
        ),
    ),
)
@method_decorator(
    name='delete',
    decorator=swagger_auto_schema(
        tags=['Machine Learning'],
        operation_summary='Remove ML Backend',
        operation_description="""
    Remove an existing ML backend connection by ID. For example, use the
    following cURL command:
    ```bash
    curl -X DELETE {host}/api/ml/{{ml_backend_ID}} -H 'Authorization: Token abc123'
    """.format(
            host=(settings.HOSTNAME or 'https://localhost:8080')
        ),
    ),
)
@method_decorator(name='put', decorator=swagger_auto_schema(auto_schema=None))
class MLBackendDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    serializer_class = MLBackendSerializer
    permission_required = all_permissions.projects_change
    queryset = MLBackend.objects.all()

    def get_object(self):
        ml_backend = super(MLBackendDetailAPI, self).get_object()
        mlgpu = MLGPU.objects.filter(ml_id=ml_backend.id).first()
        if not ComputeMarketplace.objects.filter(id=mlgpu.compute_id, type="MODEL-PROVIDER-VAST").exists():
            ml_backend.update_state()
        else:
            ml_backend.url = ml_backend.url.replace('http://', 'https://')
            # ml_backend.save()
            # check_connect_ml_vast(ml_backend.url)
            ml_backend.state = "CO"
        return ml_backend

    def perform_update(self, serializer):
        # if not permission_org(self.request.user, serializer.project):
        #     return Response("You do not have permission to perform this action.", status=status.HTTP_403_FORBIDDEN)
        
        ml_backend = serializer.save()
        ml_backend.update_state()

    def perform_destroy(self, instance):
        if not permission_org(self.request.user, instance.project):
            return Response("You do not have permission to perform this action.", status=status.HTTP_403_FORBIDDEN)
        
        return destroy_ml_instance(instance.id, self.request.user)


@method_decorator(
    name='post',
    decorator=swagger_auto_schema(
        tags=['Machine Learning'],
        operation_summary='Train',
        operation_description="""
        After you add an ML backend, call this API with the ML backend ID to start training with 
        already-labeled tasks.
        """,
        manual_parameters=[
            openapi.Parameter(
                name='id',
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_PATH,
                description='A unique integer value identifying this ML backend.'),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'use_ground_truth': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN, description='Whether to include ground truth annotations in training'
                )
            },
        ),
        responses={
            200: openapi.Response(title='Training OK', description='Training has successfully started.'),
            500: openapi.Response(
                description='Training error',
                schema=openapi.Schema(
                    title='Error message',
                    description='Error message',
                    type=openapi.TYPE_STRING,
                    example='Server responded with an error.',
                ),
            ),
        },
    ),
)
class MLBackendTrainAPI(APIView):

    permission_required = all_permissions.projects_change

    def post(self, request, *args, **kwargs):
        ml_backend = get_object_with_check_and_log(request, MLBackend, pk=self.kwargs['pk'])
        if not permission_org(self.request.user, ml_backend.project):
            return Response("You do not have permission to perform this action.", status=status.HTTP_403_FORBIDDEN)
        
        self.check_object_permissions(self.request, ml_backend)

        if ml_backend.state == "DI" or ml_backend.state == "ER":
            return  Response("No connection, please try again.", status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # check network of ml backend
        ml_network_history = MLNetworkHistory.objects.filter(
            project_id=ml_backend.project_id, ml_id = ml_backend.id, deleted_at__isnull = True
        ).first()

        # mlnetwork = MLNetwork.objects.filter(project_id=ml_backend.project_id, deleted_at__isnull = True).first()

        ml_backend_status = MLBackendStatus.objects.filter(ml_id = ml_backend.id, project_id = ml_backend.project_id, deleted_at__isnull=True).first()
        ml_network = None
        if ml_network_history is not None:
            check_master = MLBackendStatus.objects.filter(
                project_id=ml_backend.project_id,
                status="master",
                deleted_at__isnull=True,
            ).filter(
                Q(
                    ml_id__in=MLNetworkHistory.objects.filter(
                        ml_network__id=ml_network_history.ml_network_id,
                        ml_id=OuterRef("ml_id"),
                        deleted_at__isnull=True,
                    ).values("ml_id")
                )
            )

            ml_network = ml_network_history.ml_network_id
        else:
            check_master = MLBackendStatus.objects.filter(
                project_id=ml_backend.project_id,
                status="master",
                deleted_at__isnull=True,
            )

        check_node_ml = MLBackend.objects.filter(project_id = ml_backend.project_id, deleted_at__isnull=True).count()
        check_node_not_running = MLBackendStatus.objects.filter(project_id = ml_backend.project_id, deleted_at__isnull=True, status_training="join_master").count()

        from rest_framework.authtoken.models import Token
        token = Token.objects.filter(user=self.request.user)

        if check_master.exists() and ml_network_history.status == MLNetworkHistory.Status.JOINED:
            if check_master.filter(status_training = "training").exists():
                ml_backend_status.status = "worker"
                ml_backend_status.status_training = "reject_master"
                ml_backend_status.type_training = "manual"
                ml_gpu = MLGPU.objects.filter(ml_id=check_master.first().ml_id).first()
                compute_ins = ComputeMarketplace.objects.filter(id=ml_gpu.compute_id).first() 
                master_address = compute_ins.ip_address

                if compute_ins.type=="MODEL-PROVIDER-VAST":
                    from compute_marketplace.vastai_func import vast_service
                    # response_data = vast_service.get_instance_info(compute_ins.infrastructure_id)
                    response_data = vast_provider.info_compute(compute_ins.infrastructure_id)
                    master_port = response_data['instances']["ports"]["23456/tcp"][0]["HostPort"]
                else:
                    master_port = "23456"

                rank = check_node_ml-check_node_not_running
                world_size = check_node_ml

                # ml_backend_status.status_stop = "reject_master"
                # ml_backend_status.save()
            else:
                return Response({"message": "Please start training master"}, status=status.HTTP_200_OK)
        else:
            if (
                ml_backend_status
                and ml_network_history.status == MLNetworkHistory.Status.JOINED
            ):
                ml_backend_status.status = "master"
                ml_backend_status.status_training = "training"
                master_address = "127.0.0.1"
                master_port = "23456"
                rank = 0
                world_size = check_node_ml
                # ml_backend_status.type_training = "manual"
                # ml_backend_status.status_stop = "stop_master"
            else: 
                ml_backend_status.status = "worker"
                ml_backend_status.status_training = "reject_master"
                master_address = "127.0.0.1"
                master_port = "23456"
                rank = 0
                world_size = check_node_ml

        ml_backend.train(token=token.first().key, master_address = master_address, master_port = master_port, rank = rank, world_size = world_size, configs=ml_backend.config, ml_backend_id = ml_backend.id)
        ml_backend_status.save()

        serializer = MLBackendStatusSerializer(ml_backend_status)

        return Response(serializer.data, status=status.HTTP_200_OK)


@method_decorator(
    name='post',
    decorator=swagger_auto_schema(
        tags=['Machine Learning'],
        operation_summary='Stop Train',
        operation_description="""
        After you add an ML backend, call this API with the ML backend ID to start training with 
        already-labeled tasks.
        """,
        manual_parameters=[
            openapi.Parameter(
                name='id',
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_PATH,
                description='A unique integer value identifying this ML backend.'),
        ],
        responses={
            200: openapi.Response(title='Stop Training OK', description='Training has successfully started.'),
            500: openapi.Response(
                description='Training error',
                schema=openapi.Schema(
                    title='Error message',
                    description='Error message',
                    type=openapi.TYPE_STRING,
                    example='Server responded with an error.',
                ),
            ),
        },
    ),
)
class MLBackendStopTrainAPI(APIView):

    permission_required = all_permissions.projects_change

    def post(self, request, *args, **kwargs):
        ml_backend = get_object_with_check_and_log(request, MLBackend, pk=self.kwargs['pk'])
        if not permission_org(self.request.user, ml_backend.project):
            return Response("You do not have permission to perform this action.", status=status.HTTP_403_FORBIDDEN)
        
        self.check_object_permissions(self.request, ml_backend)

        if ml_backend.state == "DI" or ml_backend.state == "ER":
            return  Response("No connection, please try again.", status=status.HTTP_503_SERVICE_UNAVAILABLE)

        from rest_framework.authtoken.models import Token
        token = Token.objects.filter(user=self.request.user)
        ml_backend.stop_train(token.first().key)

        ml_backend_status = MLBackendStatus.objects.filter(ml_id = ml_backend.id, project_id = ml_backend.project_id, deleted_at__isnull=True).first()
        check_master = MLBackendStatus.objects.filter(project_id = ml_backend.project_id, status = "master", deleted_at__isnull=True)

        if check_master.exists():
            if check_master.filter(status_training = "training").exists():
                ml_backend_status.status = "worker"
                ml_backend_status.status_training = "join_master"
                ml_backend_status.type_training = "manual"
                # ml_backend_status.status_stop = "reject_master"
                # ml_backend_status.save()
            else:
                return Response({"message": "Please start training master"}, status=status.HTTP_200_OK)
        else:
            ml_backend_status.status = "master"
            ml_backend_status.status_training = "training"
            # ml_backend_status.type_training = "manual"
            # ml_backend_status.status_stop = "stop_master"
        
        ml_backend_status.save()

        serializer = MLBackendStatusSerializer(ml_backend_status)

        return Response(serializer.data, status=status.HTTP_200_OK)


@method_decorator(
    name='post',
    decorator=swagger_auto_schema(
        tags=['Machine Learning'],
        operation_summary='Request Interactive Annotation',
        operation_description="""
        Send a request to the machine learning backend set up to be used for interactive preannotations to retrieve a
        predicted region based on annotator input.
        """,
        manual_parameters=[
            openapi.Parameter(
                name='id',
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_PATH,
                description='A unique integer value identifying this ML backend.'),
        ],
        request_body=MLInteractiveAnnotatingRequest,
        responses={
            200: openapi.Response(title='Annotating OK', description='Interactive annotation has succeeded.'),
        },
    ),
)
class MLBackendInteractiveAnnotating(APIView):

    permission_required = all_permissions.tasks_view

    def post(self, request, *args, **kwargs):
        ml_backend = get_object_with_check_and_log(request, MLBackend, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, ml_backend)
        serializer = MLInteractiveAnnotatingRequest(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        task = get_object_with_check_and_log(request, Task, pk=validated_data['task'], project=ml_backend.project)
        context = validated_data.get('context')

        if flag_set('ff_back_dev_2362_project_credentials_060722_short', request.user):
            context['project_credentials_login'] = task.project.task_data_login
            context['project_credentials_password'] = task.project.task_data_password

        result = ml_backend.interactive_annotating(task, context, user=request.user)

        return Response(
            result,
            status=status.HTTP_200_OK,
        )


@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=['Machine Learning'],
        operation_summary='Get model versions',
        operation_description='Get available versions of the model.',
        responses={"200": "List of available versions."},
    ),
)
class MLBackendVersionsAPI(generics.RetrieveAPIView):

    permission_required = all_permissions.projects_change

    def get(self, request, *args, **kwargs):
        ml_backend = get_object_with_check_and_log(request, MLBackend, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, ml_backend)
        versions_response = ml_backend.get_versions()
        if versions_response.status_code == 200:
            result = {'versions': versions_response.response.get("versions", [])}
            return Response(data=result, status=200)
        elif versions_response.status_code == 404:
            result = {'versions': [ml_backend.model_version], 'message': 'Upgrade your ML backend version to latest.'}
            return Response(data=result, status=200)
        else:
            result = {'error': str(versions_response.error_message)}
            status_code = versions_response.status_code if versions_response.status_code > 0 else 500
            return Response(data=result, status=status_code)
# @method_decorator(name='get', decorator=swagger_auto_schema(
#         tags=['ML Backend Queue'],
#         operation_summary='Retrieve my queue',
#         operation_description=''
#     ))
# @method_decorator(
#         name='post',
#         decorator=swagger_auto_schema(
#             tags=['ML Backend Queue'],
#             operation_summary='',
#             operation_description="""

#             """,
#             manual_parameters=[

#             ],
#             request_body=MLBackendQueueRequest,
#             responses={
#                 200: openapi.Response(title='Task queue OK', description='Task queue has succeeded.'),
#             },
#         )
#     )
# class MLBackendQueueAPI(generics.mixins.ListModelMixin,APIView):
#     parser_classes = (JSONParser, FormParser, MultiPartParser)
#     queryset = MLBackendQueue.objects.all()
#     permission_classes = (IsAuthenticated,)
#     serializer_class = UserSerializer
#     def get_queryset(self):
#         return MLBackendQueue.objects.filter()

#     def filter_queryset(self, queryset):
#         return MLBackendQueue.objects.all()

#     def get(self, request, *args, **kwargs):
#         return Response(
#             list(MLBackendQueue.objects.values('id', 'project_id', 'task_id', 'try_count','max_tries','priority','status'))
#         )

#     def post(self, request, *args, **kwargs):
#         j_obj = json.loads(request.body)
#         # print(j_obj )
#         user = request.user
#         if int(j_obj["id"]) > 0:
#             item =MLBackendQueue.objects.filter(id=int(j_obj["id"])).first()
#             item.project_id=j_obj["project_id"]
#             item.user_id=user.id
#             item.status=j_obj["status"]
#             item.try_count=j_obj["try_count"]
#             item.max_tries=j_obj["max_tries"]
#             item.priority=j_obj["priority"]
#             item.save()
#         else:
#             MLBackendQueue.objects.create(
#                     user_id=user.id,
#                     project_id=j_obj["project_id"],
#                     task_id=j_obj["task_id"],
#                     status=j_obj["status"],
#                     try_count=j_obj["try_count"],
#                     max_tries=j_obj["max_tries"],
#                     priority=j_obj["priority"],
#                 )
#         # print(result )
#         return Response({"msg":"done"}, status=200)

@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=['Machine Learning'],
        operation_summary='List ML backends for Admin',
        operation_description="List all configured ML backends from admin view.",
        manual_parameters=[
            openapi.Parameter(
                name='project',
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_QUERY,
                description='Project ID'),
        ],
    ))
class MLBackendListAdminViewAPI(generics.ListAPIView):
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    permission_classes = (AllowAny, )
    pagination_class = SetPagination
    serializer_class = MLBackendAdminViewSerializer

    def get_queryset(self):
        project = self.request.query_params.get('project', None)
        if not project:
            return MLBackend.objects.order_by('-id')
        return MLBackend.objects.filter(project=project).order_by('-id')

    def get(self, *args, **kwargs):
        return super(MLBackendListAdminViewAPI, self).get(*args, **kwargs)

@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=['Machine Learning'],
        operation_summary='List ML backends Train job for Admin',
        operation_description="List all configured ML backends train job from admin view.",
    ))
class MLBackendTrainJobListAdminViewAPI(generics.ListAPIView):
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    permission_classes = (AllowAny, )
    pagination_class = SetPagination
    serializer_class = MLBackendTrainJobAdminViewSerializer

    def get_queryset(self):
        return MLBackendTrainJob.objects.order_by('-id')


    def get(self, *args, **kwargs):
        return super(MLBackendTrainJobListAdminViewAPI, self).get(*args, **kwargs)

@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=['Machine Learning Docker'],
        operation_summary='List ML URL using proxy',
        operation_description="List all address ML backends using nginx reverse proxy .",
        manual_parameters=[
            openapi.Parameter(
                name='project_id',
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_QUERY,
                description='Project ID'),
        ]
    ))
class MLBackendUrlViewAPI(generics.ListAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_required = ViewClassPermission(
        GET=all_permissions.projects_view,
        POST=all_permissions.projects_change,
    )
    serializer_class = ProjectMLPortSerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        project_id = self.request.query_params.get('project_id')
        queryset = ProjectMLPort.objects.filter(project_id=project_id)
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset.last(), many=False)
        return Response(serializer.data)

@method_decorator(
    name='post',
    decorator=swagger_auto_schema(
        tags=['Machine Learning'],
        operation_summary='Update Ram ML',
        operation_description="Update Ram ML.",
        manual_parameters=[
            openapi.Parameter(
                name='ml_backend_id',
                type=openapi.TYPE_NUMBER,
                in_=openapi.IN_QUERY,
                description='ML_BACKEND'),
            openapi.Parameter(
                name='ram',
                type=openapi.TYPE_NUMBER,
                in_=openapi.IN_QUERY,
                description='RAM'),
        ]
    ))
class MLBackendUpdateRam(generics.ListAPIView):
    permission_required = ViewClassPermission(
        GET=all_permissions.projects_view,
        POST=all_permissions.projects_change,
    )

    def post(self, request, *args, **kwargs):
        ml_backend_id = self.request.query_params.get("ml_backend_id")
        ram = self.request.query_params.get('ram')
        ml_backend = get_object_with_check_and_log(request, MLBackend, pk=ml_backend_id)
        self.check_object_permissions(self.request, ml_backend)

        if ml_backend.state == "DI" or ml_backend.state == "ER":
            return  Response("No connection, please try again.", status=status.HTTP_503_SERVICE_UNAVAILABLE)

        ml_backend.ram = float(ram)

        ml_backend.save()

        return Response("Update ram successfull !", status=status.HTTP_200_OK)


class MLBackendResetAPI(generics.RetrieveAPIView):
    serializer_class = MLBackendSerializer
    permission_required = (
        all_permissions.projects_change
    )  

    @swagger_auto_schema(
        tags=["Machine Learning"],
        operation_summary="Reset ML Backend - Nodes",
        operation_description="""
        Reset an existing ML backend connection by ID.
        """,
    )
    def get(self, request, *args, **kwargs):

        ml_backend_id = kwargs.get("pk")
        ml_backend = self.get_object(ml_backend_id)
        ml_backend_id = kwargs.get("pk")
        ml_backends = MLBackend.objects.filter(id=ml_backend_id).first()

        if not permission_org(self.request.user, ml_backends.project):
            return Response("You do not have permission to perform this action.", status=status.HTTP_403_FORBIDDEN)
        
        ml_backends.install_status = MLBackend.INSTALL_STATUS.REINSTALLING
        ml_backends.save()
        parsed_url = urlparse(ml_backends.url)
        ip_address = parsed_url.hostname
        ml_gpu = MLGPU.objects.filter(ml_id=ml_backend_id).first()
        if ml_gpu is None:
            Response("Not found ML GPU", status=404)
        compute = ComputeMarketplace.objects.filter(id=ml_gpu.compute_id, deleted_at__isnull = True).first()
        if compute is None:
            Response("Not found Compute", status=404)
        model = ModelMarketplace.objects.filter(id=ml_gpu.model_id).first()
        if model is None:
            Response("Not found Model", status=404)

        # handle reset with vast
        if compute.type == "MODEL-PROVIDER-VAST":
            schema = "https"
            # vast_service.delete_instance_info(compute.infrastructure_id)
            # vast_provider.delete_compute(compute.infrastructure_id)

            # status_install, response = vast_service.func_install_compute_vastai(
            #     compute.infrastructure_desc,
            #     model.docker_image,
            #     "ml",
            # )
            vast_provider.reset_compute(compute.infrastructure_id)
            # if not status_install:
            #     return Response(
            #         {"detail": f"Not available, please try again"}, status=400
            #     )
            # print(response["instances"]["ports"]["9090/tcp"][0]["HostPort"])
            # _port = response["instances"]["ports"]["9090/tcp"][0]["HostPort"]
            # compute.infrastructure_id = response["instances"]["id"]
            # compute.infrastructure_desc = response["instances"]["old_id"]
            # compute.port = _port
            # compute.save()
            # model.port = _port
            # model.save()
            # ml_gpu.port = _port
            # ml_gpu.save()
            # ml_backends.url = f"{schema}://{compute.ip_address}:{_port}"
            ml_backends.install_status = MLBackend.INSTALL_STATUS.COMPLEATED
            ml_backends.state = MLBackendState.CONNECTED
            ml_backends.save()

        else:
            # handle reset wit compute physical
            dockerContainerStartStop(
                base_image=model.docker_image,
                action="delete",
                ip_address=ip_address,
                project_id=ml_backends.project_id,
                model_id=model.pk,
            )
            compute = ComputeMarketplace.objects.filter(id=ml_gpu.compute_id).first()
            if compute is None:
                Response("Not found compute", status=404)
            _port = None
            print("compute", compute.ip_address)
            try:
                _port = createDocker(
                    model.docker_image,
                    ml_backends.project_id,
                    f"tcp://{compute.ip_address}:{compute.docker_port}",
                    model.port,
                    model.pk,
                    ml_gpu.gpus_index,
                    ml_gpu.gpus_id,
                )
                model.port = _port
                model.save()
                ml_gpu.port = _port
                ml_gpu.save()
                ml_backends.url = "http://" + model.ip_address + ":" + _port
                ml_backends.install_status = MLBackend.INSTALL_STATUS.COMPLEATED
                ml_backends.state = MLBackendState.CONNECTED
                ml_backends.save()

            except Exception as e:
                print(e)

            # Implement your logic to reset the ML backend here
            # This could involve resetting state, deleting cached data, etc.
            # For example:
            # self.state = MLBackendState.DISCONNECTED
        # update status train
        mlbackend_status = MLBackendStatus.objects.filter(ml_id=ml_backend_id).first()
        mlbackend_status.status =MLBackendStatus.Status.WORKER
        mlbackend_status.status_training = MLBackendStatus.Status.JOIN_MASTER
        mlbackend_status.save()

        return Response({"message: Reset done"}, status=status.HTTP_204_NO_CONTENT)

    def get_object(self, pk):
        try:
            return MLBackend.objects.get(pk=pk)
        except MLBackend.DoesNotExist:
            raise Response(
                "Not found ML ",
                status=status.HTTP_404_NOT_FOUND,
            )


@method_decorator(
    name="patch",
    decorator=swagger_auto_schema(
        tags=["ML"],
        operation_summary="Update ML Backend config",
        operation_description="Update ml backend config",
    ),
)
class MLBackendConfigAPI(generics.UpdateAPIView):
    serializer_class = MLUpdateConfigSerializer

    permission_required = (
        all_permissions.projects_change
    )

    def get_queryset(self):
        return MLBackend.objects.all()

    def patch(self, request, *args, **kwargs):
        ml_backend_id = self.kwargs["pk"]
        ml_backend = get_object_or_404(MLBackend, id=ml_backend_id)

        if not permission_org(self.request.user, ml_backend.project):
            return Response("You do not have permission to perform this action.", status=status.HTTP_403_FORBIDDEN)

        # Extract the new config data from the request data
        new_config = self.request.data.get("config")

        if new_config is not None:
            # Manually update the config field
            ml_backend.config = new_config
            ml_backend.save()

            return Response(new_config, status=status.HTTP_200_OK)

        return Response(
            {"detail": "Config data is required."}, status=status.HTTP_400_BAD_REQUEST
        )


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["ML"],
        operation_summary="Get ML Network",
        operation_description="Retrieve detailed information about a specific ML network backend.",
        manual_parameters=[
            openapi.Parameter(
                name="project_id",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_QUERY,
                description="project id",
                required=True
            ),
        ],
    ),
)
class MLBackendListNetworkAPI(generics.ListAPIView):
    serializer_class = MLNetworkSerializer
    permission_required = all_permissions.projects_change

    def list(self, request, *args, **kwargs):
        project_id = request.query_params.get("project_id", None)

        if project_id is None:
            return Response({"error": "Project ID is required"}, status=400)

        model_network = []
        seen_ids = set()

        ml_network_list = MLNetwork.objects.filter(
            project_id=project_id, deleted_at__isnull=True
        )

        for ml_network in ml_network_list:
            ml_network_history_list = MLNetworkHistory.objects.filter(
                project_id=project_id, deleted_at__isnull=True, ml_network_id=ml_network.id
            )
            for ml_network_history in ml_network_history_list:
                ml_backend = MLBackend.objects.filter(
                    id=ml_network_history.ml_id, deleted_at__isnull=True #is_deploy=False
                ).first()
                if ml_backend and ml_network.id not in seen_ids:
                    model_network.append({
                        "name": ml_network.name,
                        "id": ml_network.id,
                        "type": ml_network.type,
                        "routing_mode": ml_backend.routing_mode,
                        "cluster_mode": ml_backend.cluster_mode,
                        "routing_mode_status": ml_backend.routing_mode_status,
                        "routing_order": ml_backend.order
                    })
                    seen_ids.add(ml_network.id)

        response_data = {"ml_network": model_network}
        return Response(response_data)


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["ML"],
        operation_summary="Join ML Backend to Network",
        operation_description="Join a specific ML backend to an ML network.",
        manual_parameters=[
            openapi.Parameter(
                name="project_id",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_QUERY,
                description="Project ID",
                required=True,
            ),
            openapi.Parameter(
                name="ml_id",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_QUERY,
                description="ML Backend ID",
                required=True,
            ),
        ],
    ),
)
class JoinMLBackendToNetwork(APIView):
    def post(self, request, network_id):
        ml_id = request.query_params.get("ml_id")
        if not ml_id:
            return Response(
                {"error": "ML Backend ID (ml_id) is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ml_backend = get_object_or_404(MLBackend, id=ml_id, deleted_at__isnull=True)
        if not permission_org(self.request.user, ml_backend.project):
            return Response("You do not have permission to perform this action.", status=status.HTTP_403_FORBIDDEN)
        project_id = ml_backend.project_id

        # Check if there's an existing network for the project
        ml_network = MLNetwork.objects.filter(
            id=network_id, deleted_at__isnull=True
        ).first()
        if not ml_network:
            # Create a new MLNetwork if none exists
            ml_network = MLNetwork.objects.create(
                project_id=project_id,
                name=f"Network for Project {project_id}",
                model_id=ml_backend.id,
            )
            # Create a history record
            ml_network_history = MLNetworkHistory.objects.create(
                ml_network=ml_network,
                ml_id=ml_id,
                project_id=project_id,
                model_id=ml_backend.id,
                ml_gpu_id=None,
                compute_gpu_id=None,
                status=MLNetworkHistory.Status.JOINED,
            )
        else:
            ml_network_history = MLNetworkHistory.objects.filter(
                ml_id=ml_id,
                deleted_at__isnull = True
            ).first()
            if ml_network_history:
                ml_network_history.status = MLNetworkHistory.Status.JOINED
                ml_network_history.save()
            else:
                ml_network_history = MLNetworkHistory.objects.create(
                    ml_network=ml_network,
                    ml_id=ml_id,
                    project_id=project_id,
                    model_id=ml_backend.id,
                    ml_gpu_id=None,
                    compute_gpu_id=None,
                    status=MLNetworkHistory.Status.JOINED,
                )

        ml_backend_status = MLBackendStatus.objects.filter(ml_id=ml_id, deleted_at__isnull = True).first()
        ml_backend_status.status_training = MLBackendStatus.Status.JOIN_MASTER
        ml_backend_status.save()
        serializer = MLNetworkHistorySerializer(ml_network_history)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["ML"],
        operation_summary="Disconnect ML Backend from Network",
        operation_description="Disconnect a specific ML backend from an ML network.",
        manual_parameters=[
            openapi.Parameter(
                name="project_id",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_QUERY,
                description="Project ID",
                required=True,
            ),
            openapi.Parameter(
                name="ml_id",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_QUERY,
                description="ML Backend ID",
                required=True,
            ),
        ],
    ),
)
class DisconnectNetwork(APIView):
    def post(self, request, network_id):
        ml_id = request.query_params.get("ml_id")
        if not ml_id:
            return Response(
                {"error": "ML Backend ID (ml_id) is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ml_backend = get_object_or_404(MLBackend, id=ml_id, deleted_at__isnull=True)

        if not permission_org(self.request.user, ml_backend.project):
            return Response("You do not have permission to perform this action.", status=status.HTTP_403_FORBIDDEN)

        # Get the corresponding MLNetworkHistory
        ml_network_history = MLNetworkHistory.objects.filter(
            ml_id=ml_id,  deleted_at__isnull=True
        ).first()
        if  ml_network_history:
            # Update the status to disconnected
            ml_network_history.status = MLNetworkHistory.Status.DISCONNECTED
            ml_network_history.save()

        # handle reject master
        # if ml_backend.state == "DI" or ml_backend.state == "ER":
        #     return  Response("No connection, please try again.", status=status.HTTP_503_SERVICE_UNAVAILABLE)

        from rest_framework.authtoken.models import Token
        token = Token.objects.filter(user=self.request.user)
        ml_backend.stop_train(token.first().key)

        ml_backend_status = MLBackendStatus.objects.filter(ml_id = ml_backend.id, project_id = ml_backend.project_id, deleted_at__isnull=True).first()
        check_master = MLBackendStatus.objects.filter(project_id = ml_backend.project_id, status = "master", deleted_at__isnull=True)

        if check_master.exists():
            if check_master.filter(status_training = "training").exists():
                ml_backend_status.status = "worker"
                ml_backend_status.status_training = "join_master"
                ml_backend_status.type_training = "manual"
            else:
                return Response({"message": "Please start training master"}, status=status.HTTP_200_OK)
        else:
            ml_backend_status.status = "master"
            ml_backend_status.status_training = "training"
        
        ml_backend_status.save()

        serializer = MLNetworkHistorySerializer(ml_network_history)
        return Response(serializer.data, status=status.HTTP_200_OK)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["Machine Learning"],
        operation_summary="List ML backends",
        operation_description="""
    List all configured ML backends for a specific project by ID.
    Use the following cURL command:
    ```bash
    curl {host}/api/ml?project={{project_id}} -H 'Authorization: Token abc123'
    """.format(
            host=(settings.HOSTNAME or "https://localhost:8080")
        ),
        manual_parameters=[
            openapi.Parameter(
                name="project",
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_QUERY,
                description="Project ID",
            ),
            # openapi.Parameter(
            #     name="ml_network",
            #     type=openapi.TYPE_INTEGER,
            #     in_=openapi.IN_QUERY,
            #     description="ml network ID",
            # ),
        ],
    ),
)
class MLBackendDeployAPI(generics.ListCreateAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_required = ViewClassPermission(
        GET=all_permissions.projects_view,
        POST=all_permissions.projects_change,
    )
    serializer_class = MLBackendSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_interactive"] 

    def get_queryset(self):
        project_pk = self.request.query_params.get('project')
        ml_network_id = self.request.query_params.get('ml_network')
        project = get_object_with_check_and_log(self.request, Project, pk=project_pk)
        self.check_object_permissions(self.request, project)

        # Get MLBackend entries related to the project
        if ml_network_id:
            ml_backends = MLBackend.objects.filter(
                project_id=project.id,
                deleted_at__isnull=True,
                mlnetwork_id = ml_network_id,
                is_deploy = True
            ).order_by("id").all()
        else:
            ml_backends = MLBackend.objects.filter(
                project_id=project.id,
                deleted_at__isnull=True,
                is_deploy = True
            ).order_by("id").all()

        for mlb in ml_backends:
            compute_id = None
            mlgpu = MLGPU.objects.filter(ml_id=mlb.id, deleted_at__isnull=True).first()
            if mlgpu:
                compute_id = mlgpu.compute_id
            if mlb.install_status != "installing":
                mlb.update_state(compute_id)

            if mlb.state in ["DI", "ER"]:
                MLBackendStatus.objects.filter(ml_id=mlb.id, project_id=project_pk).update(status="worker", status_training="join_master")

        if ml_network_id:
            # Get MLNetwork related to the project
            ml_network = MLNetwork.objects.filter(id=ml_network_id, deleted_at__isnull=True).first()
            
            if ml_network:
                # Get MLNetworkHistory entries related to the MLNetwork
                ml_network_histories = MLNetworkHistory.objects.filter(
                    ml_network_id=ml_network.id, deleted_at__isnull=True
                ).values_list('ml_id', flat=True)

                # Filter ml_backends further based on ml_network_histories
                filtered_ml_backends = ml_backends.filter(
                    id__in=ml_network_histories
                )
                
                return filtered_ml_backends
        
        return ml_backends

    def get(self, request, *args, **kwargs):
        try:
            return super(MLBackendDeployAPI, self).get(request, *args, **kwargs)
        except Exception as e: 
            print(e)
            return Response([], status=200)

@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["Machine Learning"],
        operation_summary="List history deploy",
        operation_description="",
        manual_parameters=[
            openapi.Parameter(
                name="project",
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_QUERY,
                description="Project ID",
            ),
        ],
    ),
)
class HistoryDeployAPI(generics.ListCreateAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_required = ViewClassPermission(
        GET=all_permissions.projects_view,
        POST=all_permissions.projects_change,
    )
    serializer_class = HistoryDeploySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_interactive"] 

    def get_queryset(self):
        project_pk = self.request.query_params.get('project')
        # ml_network_id = self.request.query_params.get('ml_network')
        # project = get_object_with_check_and_log(self.request, Project, pk=project_pk)
        # self.check_object_permissions(self.request, project)

        deploy_history = History_Build_And_Deploy_Model.objects.filter(project_id=project_pk, type=History_Build_And_Deploy_Model.TYPE.DEPLOY, deleted_at__isnull=True).values_list("model_id", flat=True)
        ml_gpu = MLGPU.objects.filter(model_id__in=deploy_history).values_list("ml_id", flat=True)
        ml_backends = MLBackend.objects.filter(
            pk__in=ml_gpu,
            project_id=project_pk,
            is_deploy = True
        ).order_by("-id").all()
        if not ml_backends:
            ml_backends = MLBackend.objects.filter(
                # pk__in=ml_gpu,
                project_id=project_pk,
                deleted_at__isnull=True,
                is_deploy = False
            ).order_by("-id").all()

        return ml_backends

    def get(self, request, *args, **kwargs):
        try:
            return super(HistoryDeployAPI, self).get(request, *args, **kwargs)
        except Exception as e: 
            print(e)
            return Response([], status=200)
        
@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["ML"],
        operation_summary="Disconnect ML Backend from Network",
        operation_description="Disconnect a specific ML backend from an ML network.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "project_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="Project ID"
                ),
                "compute_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="compute_id"
                ),
                "gpu_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="gpu_id"
                )
            },
        ),
    ),
)
class AddComputeToNetwork(APIView):
    def post(self, request, *args, **kwargs):
        from model_marketplace.functions import handle_rent_model
        import threading

        project_id = request.data.get("project_id")
        gpus_data = request.data.get("gpus")
        network_id = request.data.get("network_id")
        model_type = request.data.get("model_type")
        # gpu_id = request.data.get("gpu_id")

        if not network_id or network_id == 0:
            _ml_network = MLNetwork.objects.filter(project_id=project_id, deleted_at__isnull=True).order_by("-id").first()
            model_instance = ModelMarketplace.objects.filter(id=_ml_network.model_id).first()

            max_pk = MLNetwork.objects.aggregate(Max("pk"))["pk__max"]
            if not max_pk and max_pk == 0:
                name_pk = 0
            else:
                name_pk = max_pk
                
            ml_network = MLNetwork.objects.create(
                        project_id=project_id,
                        name=f"{model_type}_{name_pk}",
                        model_id = model_instance.id,
                        type = model_type
                )
        else:
            ml_network = MLNetwork.objects.filter(id=network_id).first()
            model_instance = ModelMarketplace.objects.filter(id=ml_network.model_id).first()

        def process_compute(compute_id, gpu_id, model, ml_network):
            compute = ComputeMarketplace.objects.filter(
                id=compute_id,
            ).first()

            history_model_rent = History_Rent_Model.objects.filter(model_new_id=model.id).first()

            try:
                compute_gpu = ComputeGPU.objects.filter(id=gpu_id).first()
                compute_gpu.quantity_used += 1
                compute_gpu.save()

                gpus_index = str(ComputeGPU.objects.get(id=gpu_id).gpu_index)

                _model = model

                _port = None

                ml = MLBackend.objects.create(
                    url=f"http://{compute.ip_address}:{_model.port}",
                    project_id=project_id,
                    state=MLBackendState.DISCONNECTED,  # set connected for ml install
                    install_status=MLBackend.INSTALL_STATUS.INSTALLING,
                    mlnetwork_id=ml_network.id,
                )

                ml_gpu = MLGPU.objects.create(
                    ml_id=ml.id,
                    model_id=_model.id,
                    gpus_index=gpus_index,
                    gpus_id=gpu_id,
                    compute_id=compute.id,
                    infrastructure_id=compute.infrastructure_id,
                    model_history_rent_id=history_model_rent.id,
                    port=_port,
                )

                MLNetworkHistory.objects.create(
                    ml_network=ml_network,
                    ml_id=ml.id,
                    ml_gpu_id=ml_gpu.id,
                    project_id=project_id,
                    model_id = model.id, #model rented
                    status = MLNetworkHistory.Status.JOINED,
                    compute_gpu_id = compute_gpu.id
                )

                ml_backend_status = MLBackendStatus.objects.create(
                    ml_id= ml.id,
                    project_id = project_id,
                    status= MLBackendStatus.Status.WORKER,
                    status_training = MLBackendStatus.Status.JOIN_MASTER,
                    type_training = MLBackendStatus.TypeTraining.AUTO
                )

                history_model_rent.model_usage -= 1
                history_model_rent.type = History_Rent_Model.TYPE.RENT
                history_model_rent.save()
                ml.save()
                # Start the new thread for handle_model_provider_vast
                thread = threading.Thread(
                    target=handle_rent_model,
                    args=(
                        self,
                        compute,
                        model,
                        project_id,
                        gpus_index,
                        gpu_id,
                        _model,
                        ml,
                        ml_gpu,
                        model.docker_image,
                        ml_network.id,
                        None,
                        self.request.user,
                        model.model_source,
                        model.model_id
                    ),
                )
                thread.start()
                return

            except Exception as e:
                print(e)
                return
        
        for gpu_info in json.loads(gpus_data):
            gpu_id = gpu_info.get("gpus_id", "")
            compute_id = gpu_info.get("compute_id")
            process_compute(compute_id, gpu_id, model_instance, ml_network)

        
        return Response(status=status.HTTP_200_OK)
    
class AddRoutingModeNetwork(APIView):
    def post(self, request, *args, **kwargs):
        project_id = request.query_params.get("project_id", None)
        ml_networks = request.data.get("ml_networks")
        for ml_network in ml_networks:
            ml_backend = MLBackend.objects.filter(
                mlnetwork_id=ml_network.get("id"), project_id=project_id, deleted_at__isnull=True #is_deploy=False
            ).first()
            if ml_backend:
                update_fields = { 
                    "routing_mode": ml_network.get("routing_mode"),
                    "order": ml_network.get("order"),
                    "cluster_mode": ml_network.get("cluster_mode"),
                    "routing_mode_status": ml_network.get("routing_mode_status"),
                }

                update_fields = {k: v for k, v in update_fields.items() if v is not None}

                if update_fields:
                    for field, value in update_fields.items():
                        setattr(ml_backend, field, value)
                    ml_backend.save(update_fields=list(update_fields.keys()))

        return Response({})
