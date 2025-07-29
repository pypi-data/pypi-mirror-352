from .models import (
    ModelMarketplace,
    ModelMarketplaceLike,
    CatalogModelMarketplace,
    CheckpointModelMarketplace,
    DatasetModelMarketplace,
    ModelMarketplaceDownload,
    History_Rent_Model,
    History_Build_And_Deploy_Model,
    ModelTask,
)
from compute_marketplace.models import ComputeGPU, ComputeLogs

from .serializers import (
    ModelMarketplaceSerializer,
    UpdateMarketplaceSerializer,
    ModelMarketplaceBuySerializer,
    ModelMarketplaceLikeSerializer,
    ModelMarketplaceDownloadSerializer,
    CatalogModelMarketplaceSerializer,
    AddModelSerializer,
    ModelMarketFilter,
    CheckpointModelMarketplaceSerializer,
    DatasetModelMarketplaceSerializer,
    HistoryRentModelSerializer,
    CommercializeModelSerializer,
    HistoryRentModelListSerializer,
    DockerImageSerializer,
    HistoryBuildModelListSerializer,
    ModelTaskSerializer,
)
from core.permissions import ViewClassPermission, all_permissions
from rest_framework import generics, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema, no_body
import drf_yasg.openapi as openapi
from rest_framework.parsers import (
    FormParser,
    JSONParser,
    MultiPartParser,
    FileUploadParser,
)
from core.utils.paginate import SetPagination
from ml.models import MLBackend, MLGPU, MLBackendStatus, MLNetwork, MLNetworkHistory
from compute_marketplace.models import ComputeMarketplace, Portfolio, Trade
from projects.models import Project
from django.db.models import Q, Count, OuterRef, Subquery
from core.utils.docker_container_create import createDocker
from django_filters.rest_framework import DjangoFilterBackend
from aixblock_core.core.utils.params import get_env
import requests
from compute_marketplace.functions import notify_for_compute
from core.filters import filterModel
from core.swagger_parameters import (
    page_parameter,
    search_parameter,
    field_search_parameter,
    sort_parameter,
    type_parameter,
    field_query_parameter,
    query_value_parameter
)
from core.permissions import IsSuperAdminOrg
from organizations.models import OrganizationMember

from django.db import transaction
from users.models import User
from orders.models import Order
from datetime import datetime
import uuid
import logging
import json
from django.utils import timezone
from datetime import timedelta
from django.db.models import Max
import concurrent.futures
from model_marketplace.calc_transformer_mem import config_parser as config_cacl_mem, calc_mem
import threading
from users.service_notify import send_email_thread
from ml.functions import auto_ml_nodes
logger = logging.getLogger(__name__)
from ml.models import MLBackendState
from compute_marketplace.vastai_func import vast_service #func_install_compute_vastai, delete_instance_info
from .build_model import build_model
from .functions import handle_rent_model, handle_add_model, handle_deploy_model, get_model, calculate_memory
import uuid
import zipfile
import os 

LIST_CHECKPOINT_FORMAT = ['.pt', '.pth', '.bin', '.mar', '.pte', '.pt2', '.ptl', '.safetensors', '.onnx', '.keras', '.pb', '.ckpt', '.tflite', '.tfrecords', '.npy',
                                  '.npz', '.gguf', '.ggml', '.ggmf', '.ggjt', '.nc', '.mleap', '.coreml', '.surml', '.llamafile', '.prompt', '.pkl', '.h5', '.caffemodel', 
                                  '.prototxt', '.dlc']

@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Get Model Marketplace",
        operation_description="""
        Get task data, metadata, annotations and other attributes for a specific labeling task by task ID.
        """,
        manual_parameters=[
            openapi.Parameter(
                name="id",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_PATH,
                description="Model Marketplace ID",
            ),
        ],
    ),
)
class ModelMarketplaceByIdAPI(generics.RetrieveAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    serializer_class = ModelMarketplaceSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.model_marketplace_view,
        PATCH=all_permissions.model_marketplace_change,
        DELETE=all_permissions.model_marketplace_delete,
    )
    lookup_field = "pk"

    def get_queryset(self):
        return ModelMarketplace.objects.all()

    def get(self, request, *args, **kwargs):
        return super(ModelMarketplaceByIdAPI, self).get(request, *args, **kwargs)

    # def patch(self, request, *args, **kwargs):
    #     return super(ModelMarketplaceByIdAPI, self).patch(request, *args, **kwargs)

    # @swagger_auto_schema(auto_schema=None)
    # def put(self, request, *args, **kwargs):
    #     return super(ModelMarketplaceByIdAPI, self).put(request, *args, **kwargs)


@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Delete Model Marketplace",
        operation_description="Delete Model Marketplace!",
        manual_parameters=[
            openapi.Parameter(
                name="id",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_PATH,
                description="Model Marketplace ID",
            ),
        ],
    ),
)
class ModelMarketplaceDeleteAPI(generics.DestroyAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    serializer_class = ModelMarketplaceSerializer
    permission_required = ViewClassPermission(
        DELETE=all_permissions.model_marketplace_delete,
    )

    def get_queryset(self):
        return ModelMarketplace.objects.order_by("-id")

    def delete(self, request, *args, **kwargs):
        instance = ModelMarketplace.objects.filter(
            id = kwargs['pk']
        ).filter(
            Q(owner_id=self.request.user.id) | Q(author_id=self.request.user.id)
        ).first()

        if not instance:
            return Response({
                "detail": "You must be owner or author of model to have permission to delete this model.",
            }, status=status.HTTP_403_FORBIDDEN)

        # Call the superclass delete method
        self.perform_destroy(instance)

        try:
            ml_gpus = MLGPU.objects.filter(model_id=kwargs['pk'])
            for ml_gpu in ml_gpus:
                if MLBackend.objects.filter(id = ml_gpu.ml_id, is_deploy = False, deleted_at__isnull=True).exists():
                    MLBackendStatus.objects.filter(ml_id=ml_gpu.ml_id).update(deleted_at=timezone.now())
                    MLBackend.objects.filter(id=ml_gpu.ml_id).update(deleted_at=timezone.now())
                    ml_gpu.deleted_at = timezone.now()
                    ml_gpu.save()
        except Exception as e:
            print(e)
        return Response({"status": "success"}, status=200)


@method_decorator(
    name="patch",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Patch Update Model Marketplace",
        operation_description={
            " if is_buy_least true": {
                "author_id": 1,
                "gpus": [
                    {"compute_id": 5, "gpus_id": "10,11"},
                    {"compute_id": 3, "gpus_id": "9"},
                ],
                "cpus": [{"compute_id": 6}],
                "is_buy_least": "true",
                "project_id": 2,
            }
        },
        request_body=UpdateMarketplaceSerializer,
    ),
)
class UpdateModelMarketplaceByIdAPI(generics.UpdateAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    serializer_class = UpdateMarketplaceSerializer
    permission_required = ViewClassPermission(
        PATCH=all_permissions.model_marketplace_change,
    )
    lookup_field = "pk"

    def get_queryset(self):
        return ModelMarketplace.objects.all()

    @swagger_auto_schema(auto_schema=None)
    def put(self, request, *args, **kwargs):
        return super(UpdateModelMarketplaceByIdAPI, self).put(request, *args, **kwargs)

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        model = ModelMarketplace.objects.filter(id=self.kwargs["pk"]).first()
        user_id = self.request.user.id
        project_config = self.request.data.get("project")
        config_model = self.request.data.get("config")
        calculate_compute_gpu = self.request.data.get("calculate_compute_gpu")
        estimate_cost = self.request.data.get("estimate_cost")
        estimate_time = self.request.data.get("estimate_time")
        rent_time = self.request.data.get("rent_time")
        rent_cost = self.request.data.get("rent_cost")
        weight = self.request.data.get("weight", None)
        modeltype = self.request.data.get("modeltype", "training")

        if self.request.data.get("is_buy_least"):
            if History_Rent_Model.objects.filter(
                model_id=model.id, user_id=user_id, status="renting"
            ).exists():
                return Response(
                    {
                        "detail": "You have rented this model",
                    },
                    status=400,
                )

            start_time = timezone.now()

            if rent_time:
                time_rent_hours = int(rent_time)
                end_time = start_time + timedelta(hours=time_rent_hours)
            else:
                end_time = start_time
            project_id = self.request.data.get("project_id")
            project = Project.objects.filter(pk=project_id).first()
            if project_config and project:
                project.epochs = int(project_config["epochs"])
                project.batch_size = int(project_config["batch_size"])
                project.steps_per_epochs = int(project_config["batch_size_per_epochs"])
                project.save()
            
            flow_type = project.flow_type
            gpus_data = self.request.data.get("gpus", [])
            cpus_data = self.request.data.get("cpus", [])
            processed_compute_ids = []
            error_compute_ids = []
            error_messages = {}
            ml_network = None
            def payment_money(user_id, model):
                """
                Deduct money when buying the model then install it for compute

                Args:
                    user_id (_type_): user payment
                    model_id (_type_): model id buying
                """
                user = User.objects.get(id=user_id)
                price = model.price
                # Check the balance in the user's account
                portfolio = Portfolio.objects.get(account=user)
                if portfolio.amount_holding < price:
                    raise ValueError("Insufficient funds")
                order = Order.objects.create(
                    user=user,
                    total_amount=1,
                    price=price,
                    payment_method="wallet",
                    status="pending",
                    unit="USD",
                    payment_code=str(uuid.uuid4()),  # Generate a unique payment code
                    model_marketplace=model,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )

                trade = Trade.objects.create(
                    token_name=portfolio.token_symbol,
                    token_symbol=portfolio.token_symbol,
                    date=datetime.now(),
                    account=user,
                    amount=1,
                    price=price,
                    type="Market Fund",
                    status="completed",
                    resource="model_marketplace",
                    resource_id=model.id,
                    payment_method="wallet",
                    order=order.id,
                )
                portfolio.amount_holding -= price
                portfolio.save()

                order.status = "completed"
                order.save()

                return order, trade

            payment_money(user_id, model)

            def process_compute(compute_id, gpu_id=None, max_pk=None, max_pk_network=None):
                compute = ComputeMarketplace.objects.filter(
                    id=compute_id,
                ).first()
                if not compute:
                    error_compute_ids.append(compute_id)
                    error_messages[compute_id] = (
                        f"Compute with ID {compute_id} not found or not available for the user."
                    )
                    return
                
                try:
                    if compute_id not in processed_compute_ids:
                        # Process GPUs
                        compute_gpu = ComputeGPU.objects.filter(id=gpu_id).first()
                        if not compute_gpu:
                            error_compute_ids.append(compute_id)
                            error_messages[compute_id] = (
                                f"ComputeGPU with id {gpu_id} not found"
                            )
                            return

                        try:
                            model_config = json.loads(model.config)
                            model_weight = model_config['weights']
                            precision = [model_config.get("model_config", "float16")]
                            if weight:
                                from core.utils.convert_memory_to_byte import convert_byte_to_gb
                                
                                if isinstance(weight, dict):
                                    matching_item = weight
                                else:
                                    matching_item = next((item for item in model_weight if item["value"] == weight), None)

                                config_model["weights"] = [matching_item]
                                
                                tflop = matching_item.get("tflops", None)
                                disk_size = matching_item.get("size", None)
                                model_name = matching_item.get("value", None)
                                try:
                                    model_hf = get_model(model_name, "auto", "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")
                                    data_size = calculate_memory(model_hf, precision)[0]
                                    if flow_type == Project.FlowType.FINE_TUNE_AND_DEPLOY:
                                        disk_size = data_size["Training"]["optimizer"]
                                    else:
                                        disk_size = data_size["Infer"]
                                except Exception as e:
                                    print(e)
                                    disk_size = matching_item.get("size", None)
                                vram = matching_item.get("vram", None)
                                gpu_tflop = compute_gpu.gpu_tflops
                                gpu_disk = compute_gpu.disk
                                gpu_vram = convert_byte_to_gb(compute_gpu.gpu_memory) if compute_gpu.gpu_memory else None


                                if tflop and gpu_tflop and float(tflop) > float(gpu_tflop):
                                    error_compute_ids.append(compute_id)
                                    error_messages[compute_id] = (
                                        f"ComputeGPU with id {gpu_id} has insufficient TFLOPs.\n"
                                        f"\nRequired: {tflop} tflops, Available: {gpu_tflop} tflops."
                                    )
                                    return

                                if disk_size and gpu_disk and float(disk_size) > float(gpu_disk):
                                    error_compute_ids.append(compute_id)
                                    error_messages[compute_id] = (
                                        f"ComputeGPU with id {gpu_id} has insufficient disk size.\n"
                                        f"\nRequired: {disk_size} GB, Available: {gpu_disk} GB."
                                    )
                                    return

                                if vram and gpu_vram and float(vram) > float(gpu_vram):
                                    error_compute_ids.append(compute_id)
                                    error_messages[compute_id] = (
                                        f"ComputeGPU with id {gpu_id} has insufficient VRAM.\n"
                                        f"\nRequired: {vram} GB, Available: {gpu_vram} GB."
                                    )
                                    return

                        except Exception as e:
                            print(e)
                        
                        # return
                        # if (
                        #     project.computer_quantity_use_max
                        #     < compute_gpu.quantity_used
                        # ):
                        #     error_compute_ids.append(compute_id)
                        #     error_messages[compute_id] = (
                        #         "You have exhausted the number of model installations for the GPU"
                        #     )
                        #     return

                        # if compute_gpu.status != "renting":
                        #     error_compute_ids.append(compute_id)
                        #     error_messages[compute_id] = (
                        #         f"You cannot buy a model for computer IP {compute.ip_address} with a GPU name {compute_gpu.gpu_name} - Index {compute_gpu.gpu_index}"
                        #     )
                        #     return

                        compute_gpu.quantity_used += 1
                        compute_gpu.save()

                        gpus_index = ComputeGPU.objects.get(id=gpu_id).gpu_index
                        gpus_id_str = [gpu_id]
                        print("gpus_id_str", gpus_id_str)
                        gpus_index_str = [str(gpus_index)]
                        print("gpus_index_str", gpus_index_str)

                        from django.db.models import Max

                        # max_pk = ModelMarketplace.objects.aggregate(Max("pk"))[
                        #     "pk__max"
                        # ]

                        # copy model from model rent
                        # update model config = model_config
                        if not ModelMarketplace.objects.filter(pk=max_pk).exists():
                            _model = ModelMarketplace.objects.create(
                                pk=max_pk,
                                name=model.name,
                                owner_id=model.owner_id,
                                author_id=self.request.user.id,
                                model_desc=model.model_desc,
                                docker_image=model.docker_image,
                                docker_access_token=model.docker_access_token,
                                file=model.file,
                                infrastructure_id=compute.infrastructure_id,
                                ip_address=compute.ip_address,
                                port=model.port,
                                schema=model.schema,
                                config=(
                                    json.dumps(config_model)
                                    if config_model
                                    else json.dumps(model.config)
                                ),
                                model_id=model.model_id,
                                model_token=model.model_token,
                                checkpoint_id=model.checkpoint_id,
                                checkpoint_token=model.checkpoint_token,
                                checkpoint_source=model.checkpoint_source,
                                model_source=model.model_source,

                            )
                            
                            now = datetime.now()
                            date_str = now.strftime("%Y%m%d")
                            time_str = now.strftime("%H%M%S")
                            
                            version = f'{date_str}-{time_str}'

                            history_build = History_Build_And_Deploy_Model.objects.create(
                                version = version,
                                model_id = _model.pk,
                                # checkpoint_id = checkpoint_id,
                                project_id = project_id,
                                user_id = user_id,
                                type = History_Build_And_Deploy_Model.TYPE.BUILD
                            )
                        else:
                            _model = ModelMarketplace.objects.filter(pk=max_pk).first()

                        # check ml network
                        _port = None
                        schema = 'https'
                        if _model.schema:
                            schema = f"{_model.schema}".replace("://", "")
                        
                        # max_pk = max_pk_network
                        if not max_pk_network and max_pk_network == 0:
                            name_pk = 0
                        else:
                            name_pk = max_pk_network

                        ml_network = MLNetwork.objects.filter(
                            project_id=project_id,
                            name=f"{modeltype}_{name_pk}",
                            # model_id=_model.id,
                            deleted_at__isnull=True,
                        ).first()
                        if ml_network is None:
                            ml_network = MLNetwork.objects.create(
                                project_id=project_id,
                                name=f"{modeltype}_{name_pk}",
                                model_id = _model.id,
                                type = modeltype
                            )
                            
                        # ml_network = MLNetwork.objects.filter(project_id=project_id,model_id=_model.id, deleted_at__isnull = True).first()
                        # if ml_network is None:
                        #     # create ml network
                        #     ml_network = MLNetwork.objects.create(
                        #         project_id=project_id,
                        #         name=_model.name, 
                        #         model_id = _model.id,
                        #         type=modeltype
                        #     )

                        ml = MLBackend.objects.create(
                            url=f"{schema}://{compute.ip_address}:{_model.port}",
                            project_id=project_id,
                            state=MLBackendState.DISCONNECTED,  # set connected for ml install
                            install_status=MLBackend.INSTALL_STATUS.INSTALLING,
                            mlnetwork=ml_network,
                        )

                        ModelMarketplace.objects.filter(id=_model.pk).update(ml_id=ml.id)
                        history_rent = History_Rent_Model.objects.filter(
                            model_id=model.id,
                            user_id=user_id,
                            status="renting",
                            project_id=project_id,
                        ).first()
                        if history_rent is not None:
                            new_model_new_id = (
                                f"{history_rent.model_new_id},{_model.id}"
                                if history_rent.model_new_id
                                else str(_model.id)
                            )

                            history_rent.model_new_id = new_model_new_id
                            history_rent.model_usage -= 1
                            history_rent.save()

                        if history_rent is None:
                            history_rent = History_Rent_Model.objects.create(
                                model_id=model.id,
                                model_new_id=_model.id,
                                user_id=user_id,
                                model_usage=5,
                                project_id=project_id,
                                time_start=start_time,
                                time_end=end_time,
                                status="renting",
                                type= History_Rent_Model.TYPE.RENT,
                            )

                        ml_gpu = MLGPU.objects.create(
                            ml_id=ml.id,
                            model_id=_model.id,
                            gpus_index=gpus_index,
                            gpus_id=gpu_id,
                            compute_id=compute.id,
                            infrastructure_id=compute.infrastructure_id,
                            port=_port,
                            model_history_rent_id=history_rent.id,
                        )

                        MLNetworkHistory.objects.create(
                            ml_network=ml_network,
                            ml_id=ml.id,
                            ml_gpu_id=ml_gpu.id,
                            project_id=project_id,
                            model_id = _model.id, #model rented
                            status = MLNetworkHistory.Status.JOINED,
                            compute_gpu_id = compute_gpu.id
                        )

                        ml_backend_status = MLBackendStatus.objects.create(
                            ml_id=ml.id,
                            project_id=project_id,
                            status=MLBackendStatus.Status.WORKER,
                            status_training=MLBackendStatus.Status.JOIN_MASTER,
                            type_training=MLBackendStatus.TypeTraining.AUTO,
                        )

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
                                _model.docker_image,
                                ml_network.id,
                                model.model_id,
                                self.request.user,
                                model.model_source,
                                model.model_id
                            ),
                        )
                        thread.start()
                        # try:
                        #     send_to = [request.user.username] if request.user.username else [request.user.email]

                        #     from users.service_notify import notify_reponse
                        #     data = {
                        #             "subject": "Successfully hired model",
                        #             "from": "no-reply@app.aixblock.io",
                        #             "to": [f"{request.user.email}"],
                        #             "html": f"<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"><title>Welcome to AIxBlock</title></head><body><p>Hi [{send_to}],</p><p>You have successfully hired Model</p><p>Thank you for choosing AIxBlock. We look forward to supporting your journey with AI and blockchain technologies.</p><p>Best Regards,<br>The AIxBlock Team</p></body></html>",
                        #             "text": "Welcome to AIxBlock!",
                        #             "attachments": []
                        #         }
                        #     notify_reponse.send_email(data)
                        #     print('send done')
                        # except Exception as e:
                        #     print(e)

                        processed_compute_ids.append(compute_id)
                        return

                except Exception as e:
                    error_compute_ids.append(compute_id)
                    error_messages[compute_id] = (
                        f"Error processing compute instance: {str(e)}"
                    )
                    return

            max_pk = ModelMarketplace.objects.aggregate(Max("pk"))["pk__max"]
            max_pk_network = MLNetwork.objects.aggregate(Max("pk"))["pk__max"]

            if not max_pk:
                max_pk = 0

            for gpu_info in gpus_data:
                compute_id = gpu_info.get("compute_id")
                gpus = gpu_info.get("gpus_id", "").split(",")
                compute_id = gpu_info.get("compute_id")

                if MLGPU.objects.filter(compute_id=compute_id, deleted_at__isnull=True).exists() and not model.model_id:
                    error_compute_ids.append(compute_id)
                    error_messages[compute_id] = (
                        "This compute instance is running services on another project and cannot rent a new image from Docker Hub."
                    )
                    continue

                for gpu_id in gpus:
                    process_compute(compute_id, gpu_id, max_pk+1, max_pk_network)

            for cpu_info in cpus_data:
                compute_id = cpu_info.get("compute_id")
                process_compute(compute_id)

            # run auto select master, join master
            # if ml_network:
            #     auto_ml_nodes(self, project.id, ml_network.id)
            if processed_compute_ids:
                return Response(
                    {
                        "processed_compute_ids": processed_compute_ids,
                        "error_compute_ids": error_compute_ids,
                        "messages": error_messages,
                    },
                    status=200,
                )
            else:
                if error_compute_ids:
                    return Response(
                        {
                            "error_compute_ids": error_compute_ids,
                            "messages": error_messages,
                        },
                        status=400,
                    )
                else:
                    return Response(
                        {
                            "error_compute_ids": "No compute",
                            "messages": "No compute is available",
                        },
                        status=400,
                    )

        else:
            return super().patch(request, *args, **kwargs)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Get List Model Marketplace",
        operation_description="Get List Model Marketplace",
        manual_parameters=[
            page_parameter,
            search_parameter,
            field_search_parameter,
            sort_parameter,
            type_parameter,
            openapi.Parameter(
                name="catalog_ids",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                description="List of catalog IDs",
            ),
            openapi.Parameter(
                name="project_id",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="PROJECT ID",
            ),
            openapi.Parameter(
                name="task_names",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING),
                description="Task Names",
            ),
        ],
    ),
)
@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Post Model Marketplace",
    ),
)
class ModelMarketplaceAPI(generics.ListCreateAPIView):
    serializer_class = ModelMarketplaceSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.annotations_view,
        POST=all_permissions.annotations_view,
    )
    pagination_class = SetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ModelMarketFilter

    def perform_create(self, serializer):
        #     serializer.save(created_by=self.request.user)
        serializer.save()

    def post(self, request, *args, **kwargs):
        return super(ModelMarketplaceAPI, self).post(request, *args, **kwargs)

    def get_queryset(self):
        user_id = self.request.user.id
        project_id = self.request.query_params.get("project_id")
        if project_id and int(project_id) > 0:
            project = Project.objects.filter(pk=project_id).first()
            queryset = ModelMarketplace.objects.filter(
                catalog_id=project.template.catalog_model_id
            )
        else:
            queryset = ModelMarketplace.objects.all()
            queryset = queryset.filter(status=ModelMarketplace.Status.IN_PROGRESS)
        
        if not self.request.user.is_superuser:
            queryset = queryset.exclude(status=ModelMarketplace.Status.IN_PROGRESS, owner_id=user_id)
            
        sort = self.request.GET.get("sort")
        try:
            if "download" in sort:
                queryset = queryset.annotate(
                    download=Count("modelmarketplacedownload"),
                )

            if "like" in sort:
                queryset = queryset.annotate(like=Count("modelmarketplacelike"))
        except Exception as e:
            logger.error(e)

        catalog_id = self.request.query_params.get("catalog_id")

        if catalog_id:
            queryset.filter(catalog_ids=catalog_id)

        catalog_ids = [
            int(id)
            for id in self.request.query_params.get("catalog_ids", "").split(",")
            if id
        ]
        if catalog_ids:
            queryset.filter(catalog_id__in=catalog_ids)

        task_names = self.request.query_params.get('task_names')

        if task_names and len(task_names) > 0:
            queryset = queryset.filter(tasks__name__in=task_names.split(",")).distinct()

        return filterModel(self, queryset, ModelMarketplace)

    def get(self, request, *args, **kwargs):
        access_token = ""  # get_env('MASTER_TOKEN','')
        if access_token != "":
            endpoint = get_env("MASTER_NODE", "https://app.aixblock.io")
            headers = {f"Authorization": "access_token {access_token}"}
            response = requests.get(
                f"{endpoint}/api/model_marketplace/", headers=headers
            )
            if response.status_code == 200:
                return response.json()
            else:
                return Response({"count": 0, "results": []}, status=200)

        response = super().get(request, *args, **kwargs)
        # queryset = self.get_queryset()
        data = response.data

        data["results"] = [
            {
                **item,
                "can_rent": self.check_can_rent(
                    self.request.query_params.get("project_id"), item["id"]
                ),
            }
            for item in response.data["results"]
        ]

        return Response(data, status=response.status_code)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user_id"] = self.request.user.id
        return context

    def check_can_rent(self, project_id, model_id):
        # Check if there are any records in History_Rent_Model that match
        if project_id:
            history_record = History_Rent_Model.objects.filter(
                project_id=project_id,
                model_id=model_id,
                status=History_Rent_Model.Status.RENTING,
            ).exists()
            return (
                not history_record
            )  
        return True 


class ModelMarketplaceResolveAPI(generics.UpdateAPIView):
    permission_required = ViewClassPermission(
        PATCH=all_permissions.annotations_view,
    )

    def get_queryset(self):
        ModelMarketplace_pk = self.request.data.get("id")
        project_pk = self.request.query_params.get("project")
        return ModelMarketplace.objects.filter(id=ModelMarketplace_pk)

    def patch(self, request, *args, **kwargs):
        ModelMarketplace = self.get_object()

        if ModelMarketplace is not None:
            # ModelMarketplace.is_resolved = request.data.get('is_resolved')
            # ModelMarketplace.save(update_fields=frozenset(['is_resolved']))
            return Response(ModelMarketplaceSerializer(ModelMarketplace).data)

        return Response(status=404)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Get Model Marketplace",
        operation_description="""
        Get Model data by Catalog Model Marketplace ID.
        """,
        manual_parameters=[
            openapi.Parameter(
                name="id",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_PATH,
                description="Catalog Model Marketplace ID",
            ),
        ],
    ),
)
@method_decorator(
    name="patch",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Update Model Marketplace",
        operation_description="Update the attributes of an existing labeling task.",
        manual_parameters=[
            openapi.Parameter(
                name="id",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_PATH,
                description="Model Marketplace ID",
            ),
        ],
        request_body=ModelMarketplaceSerializer,
    ),
)
@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Delete Catalog Model Marketplace",
        operation_description="Delete a task in AiXBlock. This action cannot be undone!",
        manual_parameters=[
            openapi.Parameter(
                name="id",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_PATH,
                description="Model Marketplace ID",
            ),
        ],
    ),
)
@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Post Catalog Model Marketplace",
        operation_description="Perform an action with the selected items from a specific view.",
    ),
)
@method_decorator(
    name="put",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Post Catalog Model Marketplace",
        operation_description="Perform an action with the selected items from a specific view.",
    ),
)
class CatalogModelMarketplaceAPI(generics.ListCreateAPIView):
    serializer_class = ModelMarketplaceSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.annotations_view,
        POST=all_permissions.annotations_view,
    )

    def get_queryset(self):
        # project_pk = self.request.query_params.get('project')
        # annotation_pk = self.request.query_params.get('annotation')
        ordering = self.request.query_params.get("ordering")
        return ModelMarketplace.objects.order_by(ordering)

    def get(self, request, *args, **kwargs):
        return super(CatalogModelMarketplaceAPI, self).get(request, *args, **kwargs)

    def perform_create(self, serializer):
        # serializer.save(created_by=self.request.user)
        serializer.save()

    def post(self, request, *args, **kwargs):
        return super(CatalogModelMarketplaceAPI, self).post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super(CatalogModelMarketplaceAPI, self).delete(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return super(CatalogModelMarketplaceAPI, self).patch(request, *args, **kwargs)

    # @swagger_auto_schema(auto_schema=None)
    def put(self, request, *args, **kwargs):
        return super(CatalogModelMarketplaceAPI, self).put(request, *args, **kwargs)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["Checkpoint Model Marketplace"],
        operation_summary="Get Model Marketplace",
        operation_description="""
        Get Model data by Catalog Model Marketplace ID.
        """,
        manual_parameters=[
            openapi.Parameter(
                name="model_id",
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_QUERY,
                description="Model ID",
            ),
            openapi.Parameter(
                name="project_id",
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_QUERY,
                description="Project ID",
            ),
            openapi.Parameter(
                name="catalog_id",
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_QUERY,
                description="Catalog ID",
            ),
            openapi.Parameter(
                name="ml_id",
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_QUERY,
                description="Machine Learning ID",
            ),
        ],
    ),
)
@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["Checkpoint Model Marketplace"],
        operation_summary="Post Catalog Model Marketplace",
        operation_description="Perform an action with the selected items from a specific view.",
    ),
)
class CheckpointModelMarketplaceAPI(generics.ListCreateAPIView):
    serializer_class = CheckpointModelMarketplaceSerializer

    permission_required = ViewClassPermission(
        GET=all_permissions.model_marketplace_view,
        POST=all_permissions.model_marketplace_view,
    )

    def get_queryset(self):
        queryset = CheckpointModelMarketplace.objects.all()
        query_params = self.request.query_params
        ml_id = query_params.get("ml_id")
        catalog_id = query_params.get("catalog_id")
        model_id = query_params.get("model_id")
        project_id = query_params.get("project_id")
        checkpoint_s3 = query_params.get("checkpoint_s3")
        filters = {}
        if ml_id:
            filters["ml_id"] = ml_id
        if catalog_id:
            filters["catalog_id"] = catalog_id
        if model_id:
            filters["model_id"] = model_id
        if project_id:
            filters["project_id"] = project_id

        if filters:
            queryset = queryset.filter(**filters)
        
        if checkpoint_s3 and checkpoint_s3=="True":
            queryset = queryset.exclude(type="HUGGING_FACE")

        return queryset

    def get(self, request, *args, **kwargs):
        return super(CheckpointModelMarketplaceAPI, self).get(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save()

    def post(self, request, *args, **kwargs):

        return super(CheckpointModelMarketplaceAPI, self).post(request, *args, **kwargs)


@method_decorator(
    name="patch",
    decorator=swagger_auto_schema(
        tags=["Checkpoint Model Marketplace"],
        operation_summary="Update Model Marketplace",
        operation_description="Update the attributes of an existing labeling task.",
        manual_parameters=[
            openapi.Parameter(
                name="id",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_PATH,
                description="Model Marketplace ID",
            ),
        ],
        request_body=CheckpointModelMarketplaceSerializer,
    ),
)
@method_decorator(
    name="put",
    decorator=swagger_auto_schema(
        tags=["Checkpoint Model Marketplace"],
        operation_summary="Post Catalog Model Marketplace",
        operation_description="Perform an action with the selected items from a specific view.",
    ),
)
class CheckpointModelMarketplaceUpdateAPI(generics.UpdateAPIView):
    serializer_class = CheckpointModelMarketplaceSerializer

    permission_required = ViewClassPermission(
        PATCH=all_permissions.model_marketplace_change,
        PUT=all_permissions.model_marketplace_change,
    )

    def get_queryset(self):
        return CheckpointModelMarketplace.objects.order_by("-id")

    def patch(self, request, *args, **kwargs):
        checkpoint_id = kwargs['pk']
        project_id = self.request.data["project_id"]
        ml_backend = MLBackend.objects.filter(project_id=project_id).first()
        if not ml_backend:
            return Response("There is not model is running")
        ml_gpu = MLGPU.objects.filter(ml_id=ml_backend.id).first()
        ModelMarketplace.objects.filter(id=ml_gpu.model_id).update(checkpoint_storage_id=checkpoint_id)

        return Response("Updating checkpoint is success!")
        # return super(CheckpointModelMarketplaceUpdateAPI, self).patch(
        #     request, *args, **kwargs
        # )

    def put(self, request, *args, **kwargs):
        return super(CheckpointModelMarketplaceUpdateAPI, self).put(
            request, *args, **kwargs
        )


@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        tags=["Checkpoint Model Marketplace"],
        operation_summary="Delete Checkpoint Model Marketplace",
        operation_description="Delete a task in AiXBlock. This action cannot be undone!",
        manual_parameters=[
            openapi.Parameter(
                name="id",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_PATH,
                description="Model Marketplace ID",
            ),
        ],
    ),
)
class CheckpointModelMarketplaceDeleteAPI(generics.DestroyAPIView):
    serializer_class = CheckpointModelMarketplaceSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_required = ViewClassPermission(
        DELETE=all_permissions.model_marketplace_delete
    )

    def get_queryset(self):
        return CheckpointModelMarketplace.objects.order_by("-id")

    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["Dataset Model Marketplace"],
        operation_summary="Get Model Marketplace",
        operation_description="""
        Get Model data by Catalog Model Marketplace ID.
        """,
        manual_parameters=[
            openapi.Parameter(
                name="model_id",
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_QUERY,
                description="Model Marketplace ID",
            ),
            openapi.Parameter(
                name="project_id",
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_QUERY,
                description="Project ID",
            ),
            openapi.Parameter(
                name="catalog_id",
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_QUERY,
                description="Catalog Model Marketplace ID",
            ),
        ],
    ),
)
@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["Dataset Model Marketplace"],
        operation_summary="Post Catalog Model Marketplace",
        operation_description="Perform an action with the selected items from a specific view.",
    ),
)
class DatasetModelMarketplaceAPI(generics.ListCreateAPIView):
    serializer_class = DatasetModelMarketplaceSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.annotations_view,
        POST=all_permissions.annotations_view,
    )

    def get_queryset(self):
        queryset = DatasetModelMarketplace.objects.all()
        query_params = self.request.query_params
        ml_id = query_params.get("ml_id")
        catalog_id = query_params.get("catalog_id")
        model_id = query_params.get("model_id")
        project_id = query_params.get("project_id")

        filters = {}
        if ml_id:
            filters["ml_id"] = ml_id
        if catalog_id:
            filters["catalog_id"] = catalog_id
        if model_id:
            filters["model_id"] = model_id
        if project_id:
            filters["project_id"] = project_id

        if filters:
            queryset = queryset.filter(**filters)

        return queryset

    def get(self, request, *args, **kwargs):
        return super(DatasetModelMarketplaceAPI, self).get(request, *args, **kwargs)

    def perform_create(self, serializer):
        # serializer.save(created_by=self.request.user)
        serializer.save()

    def post(self, request, *args, **kwargs):
        return super(DatasetModelMarketplaceAPI, self).post(request, *args, **kwargs)


@method_decorator(
    name="patch",
    decorator=swagger_auto_schema(
        tags=["Dataset Model Marketplace"],
        operation_summary="Update Model Marketplace",
        operation_description="Update the attributes of an existing labeling task.",
        manual_parameters=[
            openapi.Parameter(
                name="id",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_PATH,
                description="Model Marketplace ID",
            ),
        ],
        request_body=ModelMarketplaceSerializer,
    ),
)
@method_decorator(
    name="put",
    decorator=swagger_auto_schema(
        tags=["Dataset Model Marketplace"],
        operation_summary="Post Catalog Model Marketplace",
        operation_description="Perform an action with the selected items from a specific view.",
    ),
)
class DatasetModelMarketplaceUpdateAPI(generics.UpdateAPIView):
    serializer_class = DatasetModelMarketplaceSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.model_marketplace_change,
        POST=all_permissions.model_marketplace_change,
    )

    def get_queryset(self):
        return DatasetModelMarketplace.objects.order_by("-id")

    def patch(self, request, *args, **kwargs):
        dataset_id = kwargs['pk']
        project_id = self.request.data["project_id"]
        ml_backend = MLBackend.objects.filter(project_id = project_id, deleted_at__isnull=True).order_by("-id").first()
        if not ml_backend:
            return Response("There is not model is running")
        ml_gpu = MLGPU.objects.filter(ml_id=ml_backend.id).first()
        ModelMarketplace.objects.filter(id=ml_gpu.model_id).update(dataset_storage_id=dataset_id)

        return Response("Updating checkpoint is success!")
        # return super(DatasetModelMarketplaceUpdateAPI, self).patch(
        #     request, *args, **kwargs
        # )

    def put(self, request, *args, **kwargs):
        return super(DatasetModelMarketplaceUpdateAPI, self).put(
            request, *args, **kwargs
        )


@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        tags=["Dataset Model Marketplace"],
        operation_summary="Delete DataSet Model Marketplace",
        operation_description="Delete a task in AiXBlock. This action cannot be undone!",
        manual_parameters=[
            openapi.Parameter(
                name="id",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_PATH,
                description="Model Marketplace ID",
            ),
        ],
    ),
)
class DatasetModelMarketplaceDeleteAPI(generics.DestroyAPIView):
    serializer_class = DatasetModelMarketplaceSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.annotations_view,
        POST=all_permissions.annotations_view,
    )

    def get_queryset(self):
        return DatasetModelMarketplace.objects.order_by("-id")

    def delete(self, request, *args, **kwargs):
        return super(DatasetModelMarketplaceDeleteAPI, self).delete(
            request, *args, **kwargs
        )


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Model Marketplace buy/least",
        operation_description="Model Marketplace buy/least.",
    ),
)
class ModelMarketplaceBuyAPI(generics.CreateAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    serializer_class = ModelMarketplaceBuySerializer
    permission_required = ViewClassPermission(
        POST=all_permissions.annotations_view,
    )

    def post(self, request, *args, **kwargs):
        return super(ModelMarketplaceBuyAPI, self).post(request, *args, **kwargs)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Count like of Model Marketplace",
        operation_description="Count like of Model Marketplace.",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Success", schema=ModelMarketplaceLikeSerializer
            )
        },
    ),
)
@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Like and unlike Model Marketplace",
        operation_description="Like and unlike Model Marketplace.",
        request_body=no_body,
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Success", schema=ModelMarketplaceLikeSerializer
            )
        },
    ),
)
class ModelMarketplaceLikeAPI(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    serializer_class = ModelMarketplaceLikeSerializer
    permission_required = ViewClassPermission(
        POST=all_permissions.annotations_view,
    )

    def get(self, request, model_id):
        user_id = self.request.user.id
        existing_like = ModelMarketplaceLike.objects.filter(
            model_id=model_id, user_id=user_id
        ).first()
        likes_count = ModelMarketplaceLike.objects.filter(model_id=model_id).count()
        model_using = History_Rent_Model.objects.filter(
            user_id=request.user.id, model_id=model_id, status="renting"
        ).first()

        if model_using is not None:
            model_using.check_status()

        return Response(
            {"is_like": True if existing_like else False, "like_count": likes_count},
            status=200,
        )

    def post(self, request, model_id):
        user_id = self.request.user.id
        existing_like = ModelMarketplaceLike.objects.filter(
            model_id=model_id, user_id=user_id
        ).first()
        if existing_like:
            existing_like.delete()
            model = ModelMarketplace.objects.filter(id=model_id).first()
            model.like_count -= 1
            model.save()
            is_like = False
        else:
            model = ModelMarketplace.objects.filter(id=model_id).first()
            user = get_user_model().objects.filter(id=user_id).first()
            ModelMarketplaceLike.objects.create(model_id=model, user_id=user)
            model.like_count += 1
            model.save()
            is_like = True
        return Response(
            {
                "is_like": is_like,
                "like_count": ModelMarketplaceLike.objects.filter(
                    model_id=model_id
                ).count(),
            }
        )


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Count download of Model Marketplace",
        operation_description="Count download of Model Marketplace.",
    ),
)
@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Model Marketplace download",
        operation_description="Model Marketplace download.",
        request_body=no_body,
    ),
)
class ModelMarketplaceDownloadAPI(generics.CreateAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    serializer_class = ModelMarketplaceDownloadSerializer
    permission_required = ViewClassPermission(
        POST=all_permissions.annotations_view,
    )

    def get(self, request, model_id):
        download_count = ModelMarketplaceDownload.objects.filter(
            model_id=model_id
        ).count()
        return Response({"likes": download_count})

    def post(self, request, model_id, *args, **kwargs):
        user_id = self.request.user.id
        model = ModelMarketplace.objects.filter(id=model_id).first()
        if not model:
            raise ValidationError(f"Model with id {model_id} does not exist")
        model.author_id = user_id
        model.download_count += 1
        model.save()
        request.data["model_id"] = model_id
        request.data["user_id"] = user_id
        return super(ModelMarketplaceDownloadAPI, self).post(request, *args, **kwargs)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Get Model Marketplace by seller",
        operation_description="Get Model Marketplace by seller.",
    ),
)
class ModelMarketplaceBySellerAPI(generics.ListAPIView):
    serializer_class = ModelMarketplaceSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.annotations_view,
        POST=all_permissions.annotations_view,
    )
    pagination_class = SetPagination

    def get_queryset(self):
        # ordering = self.request.query_params.get("ordering")
        user_id = self.request.user.id
        if not self.request.user.is_superuser:
            return ModelMarketplace.objects.filter(
                Q(owner_id=user_id), ~Q(type="MODEL-SYSTEM"), Q(status__in=["in_marketplace"])
            ).order_by("-id")
        else:
            return ModelMarketplace.objects.filter(
                Q(owner_id=user_id), Q(status__in=["in_marketplace"])
            ).order_by("-id")

    def get(self, request, *args, **kwargs):
        return super(ModelMarketplaceBySellerAPI, self).get(request, *args, **kwargs)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Get List Catalog Model Marketplace",
        operation_description="Get List Catalog Model Marketplace.",
        manual_parameters=[
            openapi.Parameter(
                name="filter", type=openapi.TYPE_STRING, in_=openapi.IN_QUERY
            ),
            openapi.Parameter(
                name="value", type=openapi.TYPE_STRING, in_=openapi.IN_QUERY
            ),
        ],
    ),
)
class CataLogModelMarketplaceAPI(generics.ListAPIView):
    serializer_class = CatalogModelMarketplaceSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.annotations_view,
    )

    def get_queryset(self):
        filter = self.request.GET.get("filter")
        value = self.request.GET.get("value")
        if filter == "all":
            return CatalogModelMarketplace.objects.filter(
                Q(name__icontains=value)
                | Q(tag__icontains=value)
                | Q(status__icontains=value)
            ).order_by("-id")
        if filter == "name":
            return CatalogModelMarketplace.objects.filter(
                name__icontains=value
            ).order_by("-id")
        if filter == "status":
            return CatalogModelMarketplace.objects.filter(
                status__icontains=value
            ).order_by("-id")
        if filter == "tag":
            return CatalogModelMarketplace.objects.filter(
                tag__icontains=value
            ).order_by("-id")

        return CatalogModelMarketplace.objects.order_by("-id")

    def get(self, request, *args, **kwargs):
        return super(CataLogModelMarketplaceAPI, self).get(request, *args, **kwargs)


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Add Model Marketplace",
        manual_parameters=[
            openapi.Parameter(
                "file",
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                description="Document to be uploaded",
            ),
            openapi.Parameter(
                "name",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="name",
                required=True,
            ),
            # openapi.Parameter(
            #     "docker_image",
            #     openapi.IN_FORM,
            #     type=openapi.TYPE_STRING,
            #     description="docker_image",
            #     required=True,
            # ),
            # openapi.Parameter(
            #     "docker_access_token",
            #     openapi.IN_FORM,
            #     type=openapi.TYPE_STRING,
            #     description="docker_access_token",
            #     required=True,
            # ),
            openapi.Parameter(
                "model_desc",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="model_desc",
            ),
            openapi.Parameter(
                "ip_address",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="ip_address",
            ),
            # openapi.Parameter(
            #     "port",
            #     openapi.IN_FORM,
            #     type=openapi.TYPE_STRING,
            #     description="port",
            #     required=False,
            # ),
            openapi.Parameter(
                "project_id",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="project_id",
                required=True,
            ),
            openapi.Parameter(
                "model_id",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="model_id",
                required=False,
            ),
            openapi.Parameter(
                "model_token",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="model_token",
                required=False,
            ),
            openapi.Parameter(
                "checkpoint_id",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="checkpoint_id",
                required=False,
            ),
            openapi.Parameter(
                "checkpoint_token",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="checkpoint_token",
                required=False,
            ),
            openapi.Parameter(
                "model_source",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="HUGGING_FACE,ROBOFLOW,GIT,DOCKER_HUB, LOCAL",
                required=False,
            ),
            openapi.Parameter(
                "checkpoint_source",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="HUGGING_FACE,ROBOFLOW,GIT,KAGGLE,CLOUD_STORAGE",
                required=False,
            ),
            openapi.Parameter(
                "cpus_ids",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="cpus_ids list id cpu selected - id of compute, eg:1,2,3",
            ),
            openapi.Parameter(
                "compute_id",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="compute_id",
            ),
            openapi.Parameter(
                "model_info",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="model_info",
            ),
            openapi.Parameter(
                "check_sequential_sampling_tasks",
                openapi.IN_FORM,
                type=openapi.TYPE_BOOLEAN,
                description="Sequential sampling Tasks are ordered by Data manager ordering",
                required=False,
            ),
            openapi.Parameter(
                "check_random_sampling",
                openapi.IN_FORM,
                type=openapi.TYPE_BOOLEAN,
                description="Random sampling. Tasks are chosen with uniform random",
                required=False,
            ),
            openapi.Parameter(
                "gpus", openapi.IN_FORM, type=openapi.TYPE_STRING, description="gpus"
            ),
            openapi.Parameter(
                "config",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="config ml",
            ),
        ],
        consumes=["multipart/form-data"],
    ),
)
class AddModelApi(APIView):
    parser_classes = (MultiPartParser, FileUploadParser)
    serializer_class = AddModelSerializer
    permission_required = ViewClassPermission(
        POST=all_permissions.annotations_view,
        PATCH=all_permissions.annotations_view,
    )
    permission_classes = [IsSuperAdminOrg]

    def patch(self, request, *args, **kwargs):
        obj = ModelMarketplace.objects.filter(id=self.kwargs["pk"]).first()
        try:
            body = json.loads(request.body)
            obj.name = body.get("name")
            obj.owner_id = body.get("owner_id")
            obj.author_id = body.get("author_id")
            obj.model_desc = body.get("model_desc")
            obj.port = body.get("port")
            obj.ip_address = body.get("ip_address")
            obj.docker_image = body.get("docker_image")
            obj.type = body.get("type")
            obj.model_source = body.get("model_source")
            obj.model_id = body.get("model_id")
            obj.model_token = body.get("model_token")
            obj.checkpoint_source = body.get("checkpoint_source")
            obj.checkpoint_id = body.get("checkpoint_id")
            obj.model_type = body.get("model_type")
            obj.status = body.get("status")

            model_type = body.get("model_type", "training")

            try:
                config = json.loads(body.get("config"))
            except:
                import ast
                config = ast.literal_eval(body.get("config"))

            if "TrainingArguments" in config:
                import yaml
                trainingArguments = config["TrainingArguments"]

                # Nếu trainingArguments đã là dict, không cần phân tích JSON nữa
                if isinstance(trainingArguments, dict):
                    config["TrainingArguments"] = trainingArguments
                else:
                    # Nếu không phải dict, kiểm tra nếu là định dạng JSON hợp lệ
                    try:
                        parsed_json = json.loads(trainingArguments)  # Kiểm tra JSON
                        config["TrainingArguments"] = parsed_json
                    except json.JSONDecodeError:
                        # Nếu không phải JSON hợp lệ, thử phân tích YAML
                        try:
                            parsed_yaml = yaml.safe_load(trainingArguments)  # Kiểm tra YAML
                            config["TrainingArguments"] = parsed_yaml
                        except yaml.YAMLError:
                            # Nếu cả JSON và YAML đều không hợp lệ
                            return Response({"messages": "Invalid format. Please check the input format!"}, status=400)

            obj.config = json.dumps(config)

            obj.save()
            return Response({"messages": "done"}, status=200)
        except Exception as e:
            print(e)
            return Response(
                {
                    "error_compute_ids": "No compute",
                    "messages": "Something wrongs, please contract with us",
                },
                status=400,
            )

    def post(self, request, *args, **kwargs):
        user_id = self.request.user.id
        gpus_data = json.loads(request.data.get("gpus", "[]"))
        config_ml = json.loads(request.data.get("config", "[]"))
        cpus_ids = request.data.get("cpus_ids")
        project_id = request.data.get("project_id")
        model_id = request.data.get("model_id")
        model_name = request.data.get("name")
        name  = uuid.uuid4()
        model_path = request.data.get("model_path")
        model_token = request.data.get("model_token")
        checkpoint_id = request.data.get("checkpoint_id")
        checkpoint_token = request.data.get("checkpoint_token")
        model_source = request.data.get("model_source")
        checkpoint_source = request.data.get("checkpoint_source")
        framework= request.data.get("framework")
        model_type = request.data.get("model_type", "training")
        # compute = ComputeMarketplace.objects.filter(
        #     author_id=self.request.user.id
        # ).last()
        model_info_json = json.loads(request.data.get("model_info"))
        if framework and 'framework' in model_info_json:
            model_info_json['framework'] = framework

        calculate_compute_gpu = model_info_json["calculate_compute_gpu"]
        token_length = model_info_json["token_length"]
        project_config = model_info_json["project"]
        processed_compute_ids = []
        error_compute_ids = []
        error_messages = {}
        ml_network = None

        ALLOWED_EXTENSIONS = {'zip', 'rar', 'gz', 'tar.gz'}

        def allowed_file(filename):
            # Check if the file extension is in the allowed set
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        def check_file_extension_in_list(files, extensions=LIST_CHECKPOINT_FORMAT, is_config=False):
            # if is_config:
            #     if 'config.json' not in files:
            #         return '3'
                
            for file in files:
                ext = os.path.splitext(file)[-1]  # Lấy đuôi mở rộng của file
                if ext in extensions:
                    return True
            return '2'
        
        def list_files_in_repo(repo_url, token=None, path='', check_dockerfile=False):
            headers = {}
            if token:
                headers['Authorization'] = f'token {token}'
            
            # API endpoint to list files in a specific directory
            api_url = f"{repo_url}/contents/{path}"
            
            try:
                response = requests.get(api_url, headers=headers, allow_redirects=True)
                if response.status_code == 200:
                    contents = response.json()
                    # List all files in the specified directory
                    files = [item['path'] for item in contents if item['type'] == 'file']
                    
                    if check_dockerfile:
                        if 'Dockerfile' not in files:
                            return '1'
                    else:
                        return check_file_extension_in_list(files, is_config=True)
                    return True
            except Exception as e:
                print(e)
                return True
                    
        def file_exists_in_hf_repo(model_name, token=None, path='', check_dockerfile=False, is_config=False):
            # API URL to list files in the model repository
            api_url = f"https://huggingface.co/api/models/{model_name}/tree/main"
            
            try:
                response = requests.get(api_url, allow_redirects=True)
                if response.status_code == 200:
                    contents = response.json()
                    # Check if the file_path exists in the list of files
                    files = [item['path'] for item in contents if item['type'] == 'file']
                    if check_dockerfile:
                        if 'Dockerfile' not in files:
                            return '1'
                    else:
                        return check_file_extension_in_list(files, is_config=is_config)
                    return True
            except Exception as e:
                print(e)
                return True

        def check_files_in_zip(file, check_dockerfile=False):
            try:
                with zipfile.ZipFile(file, 'r') as zip_ref:
                    zip_file_list = zip_ref.namelist()
                    if check_dockerfile: 
                        # if not any(file_path.endswith('Dockerfile') for file_path in zip_file_list):
                        if not any(file_path == "Dockerfile" for file_path in zip_file_list):
                            return '1'
                    else:
                        for zip_file in zip_file_list:
                            ext = os.path.splitext(zip_file)[-1].lower()
                            if ext in LIST_CHECKPOINT_FORMAT:
                                return True
                        return '2'
                            
                    return True
            except zipfile.BadZipFile:
                return False
        
        def check_grpc_usage_in_file(repo_url, token=None, file_name=None):
            import base64
            if not file_name:
                return False, 
            contains_ssl = False
            headers = {}
            if token:
                headers['Authorization'] = f'token {token}'
            
            # API URL để đọc nội dung file Python
            file_api_url = f"{repo_url}/contents/{file_name}"
            
            try:
                response = requests.get(file_api_url, headers=headers)
                if response.status_code == 200:
                    content_data = response.json()
                    if content_data['type'] == 'file':
                        # Giải mã nội dung file từ Base64
                        file_content = base64.b64decode(content_data['content']).decode('utf-8')
                        ssl_patterns = [
                            r"ssl_context\s*=",  # Flask (app.run(ssl_context=...))
                            r"certfile\s*=",      # FastAPI / Uvicorn
                            r"keyfile\s*=",
                            r"ssl\.SSLContext",
                            r"ssl\.wrap_socket",
                            r"\.crt",            
                            r"\.pem"
                        ]

                        contains_ssl = any(re.search(pattern, file_content) for pattern in ssl_patterns)
                        
                        # Kiểm tra xem có sử dụng gRPC trong file không
                        if 'import grpc' in file_content or 'from grpc' in file_content:
                            return True, contains_ssl
                    return False, contains_ssl
                else:
                    print(f"Lỗi khi lấy file: {response.status_code}, {response.text}")
                    return False, contains_ssl
            except Exception as e:
                print(f"Exception occurred: {e}")
                return False, contains_ssl
        
        def check_grpc_usage_in_file_hf(repo_url, token=None, file_name=None):
            if not file_name:
                return False
            contains_ssl = False
            headers = {}
            if token:
                headers['Authorization'] = f'Bearer {token}'
            
            # API URL để đọc nội dung file Python
            file_api_url = f"{repo_url}/raw/main/{file_name}"
            
            try:
                response = requests.get(file_api_url, headers=headers)
                if response.status_code == 200:
                    file_content = response.text
                    ssl_patterns = [
                        r"ssl_context\s*=",  # Flask (app.run(ssl_context=...))
                        r"certfile\s*=",      # FastAPI / Uvicorn
                        r"keyfile\s*=",
                        r"ssl\.SSLContext",   # Sử dụng module ssl
                        r"ssl\.wrap_socket",
                        r"\.crt",             # File chứng chỉ
                        r"\.pem"
                    ]

                    contains_ssl = any(re.search(pattern, file_content) for pattern in ssl_patterns)
                    
                    # Kiểm tra xem có sử dụng gRPC trong file không
                    if 'import grpc' in file_content or 'from grpc' in file_content:
                        return True, contains_ssl
                    
                    return False, contains_ssl
                else:
                    print(f"Lỗi khi lấy file: {response.status_code}, {response.text}")
                    return False, contains_ssl
            except Exception as e:
                print(f"Exception occurred: {e}")
                return False, contains_ssl

        def check_grpc_usage_in_uploaded_file(zip_file_content, file_name=None):
            import io
            if not file_name:
                return False
            
            contains_ssl = False
            try:
                with zipfile.ZipFile(io.BytesIO(zip_file_content), 'r') as zip_ref:
                    # Đảm bảo rằng file tồn tại trong ZIP
                    if file_name in zip_ref.namelist():
                        with zip_ref.open(file_name) as file:
                            file_content = file.read().decode('utf-8')
                            ssl_patterns = [
                                r"ssl_context\s*=",  # Flask (app.run(ssl_context=...))
                                r"certfile\s*=",      # FastAPI / Uvicorn
                                r"keyfile\s*=",
                                r"ssl\.SSLContext",   # Sử dụng module ssl
                                r"ssl\.wrap_socket",
                                r"\.crt",             # File chứng chỉ
                                r"\.pem"
                            ]

                            contains_ssl = any(re.search(pattern, file_content) for pattern in ssl_patterns)

                            # Kiểm tra xem có sử dụng gRPC trong file không
                            if 'import grpc' in file_content or 'from grpc' in file_content:
                                return True, contains_ssl
                            
                return False, contains_ssl
            except Exception as e:
                print(f"Exception occurred: {e}")
                return False, contains_ssl

        def read_dockerfile_content_from_uploaded(zip_file_content):
            import io
            import re
            try:
                with zipfile.ZipFile(io.BytesIO(zip_file_content), 'r') as zip_ref:
                    # Kiểm tra sự tồn tại của Dockerfile trong ZIP
                    dockerfile_content = None
                    for file_name in zip_ref.namelist():
                        if 'Dockerfile' in file_name:
                            with zip_ref.open(file_name) as file:
                                dockerfile_content = file.read().decode('utf-8')
                                break

                    if not dockerfile_content:
                        return {
                            'run_command': "Không tìm thấy Dockerfile trong file ZIP.",
                            'exposed_ports': [],
                            'grpc_used': False
                        }

                    # Tìm các lệnh CMD hoặc ENTRYPOINT
                    cmd_match = re.findall(r'^CMD\s+(.*)', dockerfile_content, re.MULTILINE)
                    entrypoint_match = re.findall(r'^ENTRYPOINT\s+(.*)', dockerfile_content, re.MULTILINE)

                    # Gộp tất cả lệnh CMD và ENTRYPOINT
                    commands = cmd_match + entrypoint_match
                    run_command = None

                    # Lọc và xử lý để trả về chính xác lệnh chạy
                    for command in commands:
                        # Loại bỏ CMD/ENTRYPOINT và các ký tự không cần thiết như [], " hoặc '
                        cleaned_command = re.sub(r'^\[|\]$', '', command).strip()
                        cleaned_command = cleaned_command.replace('"', '').replace("'", "")

                        # Nếu lệnh chứa dấu phẩy, kết hợp lại thành chuỗi
                        if ',' in cleaned_command:
                            cleaned_command = ' '.join(cleaned_command.split(','))

                        # Chỉ lấy phần lệnh chạy chính (bỏ exec nếu có)
                        if cleaned_command.startswith("exec "):
                            cleaned_command = cleaned_command[5:].strip()

                        # Trả về lệnh nếu nó có chứa python hoặc gunicorn
                        if "python" in cleaned_command or "gunicorn" in cleaned_command:
                            run_command = cleaned_command
                            break

                    # Kiểm tra các cổng expose trong Dockerfile
                    exposed_ports = re.findall(r'EXPOSE\s+([0-9\s]+)', dockerfile_content)
    
                    # Tách tất cả các cổng ra từ chuỗi, và loại bỏ khoảng trắng
                    ports_list = exposed_ports[0].split() if exposed_ports else []

                    grpc_used = False
                    ssl_used = False

                    if run_command and "python" in run_command:
                        # Lấy tên file Python thực thi từ lệnh chạy (ví dụ: "python app.py")
                        python_file = re.findall(r'python(?:\d+(?:\.\d+)*)?\s+(\S+)', run_command)
                        if python_file:
                            grpc_used, ssl_used = check_grpc_usage_in_uploaded_file(zip_file_content, python_file[0])

                    # Trả về kết quả với lệnh chạy và các cổng expose
                    return {
                        'run_command': run_command if run_command else None,
                        'exposed_ports': ports_list if ports_list else None,
                        'grpc_used': grpc_used,
                        'ssl_used': ssl_used
                    }

            except Exception as e:
                print(f"Exception occurred: {e}")
                return {
                    'run_command': "Lỗi khi đọc Dockerfile trong file ZIP.",
                    'exposed_ports': [],
                    'grpc_used': False
                }
            
        def read_file_content_from_hf(model_id, token=None, file_path=''):
            import re
            headers = {}
            repo_url = f"https://huggingface.co/{model_id}"
            
            if token:
                headers['Authorization'] = f'Bearer {token}'
            
            # API endpoint để lấy nội dung file
            api_url = f"{repo_url}/resolve/main/{file_path}"
            
            try:
                response = requests.get(api_url, headers=headers)
                if response.status_code == 200:
                    file_content = response.text
                    
                    # Tìm các lệnh CMD hoặc ENTRYPOINT (trong trường hợp là Dockerfile)
                    cmd_match = re.findall(r'^CMD\s+(.*)', file_content, re.MULTILINE)
                    entrypoint_match = re.findall(r'^ENTRYPOINT\s+(.*)', file_content, re.MULTILINE)
                    
                    # Gộp tất cả lệnh CMD và ENTRYPOINT
                    commands = cmd_match + entrypoint_match
                    run_command = None
                    
                    # Lọc và xử lý để trả về chính xác lệnh chạy
                    for command in commands:
                        # Loại bỏ CMD/ENTRYPOINT và các ký tự không cần thiết như [], " hoặc '
                        cleaned_command = re.sub(r'^\[|\]$', '', command).strip()
                        cleaned_command = cleaned_command.replace('"', '').replace("'", "")

                        # Nếu lệnh chứa dấu phẩy, kết hợp lại thành chuỗi
                        if ',' in cleaned_command:
                            cleaned_command = ' '.join(cleaned_command.split(','))

                        # Chỉ lấy phần lệnh chạy chính (bỏ exec nếu có)
                        if cleaned_command.startswith("exec "):
                            cleaned_command = cleaned_command[5:].strip()

                        # Trả về lệnh nếu nó có chứa python hoặc gunicorn
                        if "python" in cleaned_command or "gunicorn" in cleaned_command:
                            run_command = cleaned_command
                            break
                    
                    exposed_ports = re.findall(r'EXPOSE\s+([0-9\s]+)', file_content)
    
                    # Tách tất cả các cổng ra từ chuỗi, và loại bỏ khoảng trắng
                    ports_list = exposed_ports[0].split() if exposed_ports else []


                    grpc_used = False
                    if run_command and "python" in run_command:
                        # Lấy tên file Python thực thi từ lệnh chạy (ví dụ: "python app.py")
                        python_file = re.findall(r'python(?:\d+(?:\.\d+)*)?\s+(\S+)', run_command)
                        if python_file:
                            grpc_used, ssl_used = check_grpc_usage_in_file_hf(repo_url, token, python_file[0])
                    
                    # Trả về kết quả với lệnh chạy và các cổng expose
                    return {
                        'run_command': run_command if run_command else None,
                        'exposed_ports': ports_list if ports_list else None,
                        'grpc_used': grpc_used,
                        'ssl_used': ssl_used
                    }
                
                else:
                    print(f"Error: {response.status_code}, {response.text}")
                    return None
                
            except Exception as e:
                print(f"Exception occurred: {e}")
                return None
            
        def read_file_content_from_repo(repo_url, token=None, file_path=''):
            import base64
            import re
            headers = {}
            repo_url = repo_url.replace("https://github.com/", "https://api.github.com/repos/")
            repo_url = repo_url.removesuffix(".git")
            if token:
                headers['Authorization'] = f'token {token}'
            
            # API endpoint để lấy nội dung file
            api_url = f"{repo_url}/contents/{file_path}"
            
            try:
                response = requests.get(api_url, headers=headers)
                if response.status_code == 200:
                    content_data = response.json()
                    if content_data['type'] == 'file':
                        # Giải mã nội dung Base64
                        dockerfile_content = base64.b64decode(content_data['content']).decode('utf-8')
                        
                        # Tìm các lệnh CMD hoặc ENTRYPOINT
                        cmd_match = re.findall(r'^CMD\s+(.*)', dockerfile_content, re.MULTILINE)
                        entrypoint_match = re.findall(r'^ENTRYPOINT\s+(.*)', dockerfile_content, re.MULTILINE)
                        
                        # Gộp tất cả lệnh CMD và ENTRYPOINT
                        commands = cmd_match + entrypoint_match
                        run_command = None
                        
                        # Lọc và xử lý để trả về chính xác lệnh chạy
                        for command in commands:
                            # Loại bỏ CMD/ENTRYPOINT và các ký tự không cần thiết như [], " hoặc '
                            cleaned_command = re.sub(r'^\[|\]$', '', command).strip()
                            cleaned_command = cleaned_command.replace('"', '').replace("'", "")

                            # Nếu lệnh chứa dấu phẩy, kết hợp lại thành chuỗi
                            if ',' in cleaned_command:
                                cleaned_command = ' '.join(cleaned_command.split(','))

                            # Chỉ lấy phần lệnh chạy chính (bỏ exec nếu có)
                            if cleaned_command.startswith("exec "):
                                cleaned_command = cleaned_command[5:].strip()

                            # Trả về lệnh nếu nó có chứa python hoặc gunicorn
                            if "python" in cleaned_command or "gunicorn" in cleaned_command:
                                run_command = cleaned_command
                                break
                        
                         # Tìm các cổng expose trong Dockerfile
                        exposed_ports = re.findall(r'^(?!#)\s*EXPOSE\s+([0-9\s]+)', dockerfile_content, re.MULTILINE)
    
                        # Tách tất cả các cổng ra từ chuỗi, và loại bỏ khoảng trắng
                        ports_list = exposed_ports[0].split() if exposed_ports else []

                        grpc_used = False
                        if run_command and "python" in run_command:
                            # Lấy tên file Python thực thi từ lệnh chạy (ví dụ: "python app.py")
                            python_file = re.findall(r'python(?:\d+(?:\.\d+)*)?\s+(\S+)', run_command)
                            if python_file:
                                grpc_used, ssl_used = check_grpc_usage_in_file(repo_url, token, python_file[0])
                        
                        
                        # Trả về kết quả với lệnh chạy và các cổng expose
                        return {
                            'run_command': run_command if run_command else None,
                            'exposed_ports': ports_list if ports_list else None,
                            'grpc_used': grpc_used,
                            'ssl_used': ssl_used
                        }
                            
                else:
                    print(f"Error: {response.status_code}, {response.text}")
                    return None
                
            except Exception as e:
                print(f"Exception occurred: {e}")
                return None
         
        file = request.data.get("file")
        zip_file_content = None
        project = Project.objects.get(pk=int(project_id))

        def check_git_repo_exists(repo_url, token=None, check_dockerfile=False):
            headers = {}
            repo_url = repo_url.replace("https://github.com/", "https://api.github.com/repos/")
            repo_url = repo_url.removesuffix(".git")

            if token:
                headers['Authorization'] = f'token {token}'

            try:
                response = requests.get(repo_url, headers=headers, allow_redirects=True)
                if response.status_code == 200: 
                    status = list_files_in_repo(repo_url, token, check_dockerfile=check_dockerfile)
                    return status
                elif response.status_code == 404:
                    return False
                else:
                    # return True
                    response.raise_for_status()

            except Exception as e:
                print(e)
                return False

        def check_docker_image_exists(image_name, token=None):
            # Tách tên repo và tag từ image_name
            if ':' in image_name:
                repo_name, tag = image_name.split(':')
            else:
                repo_name = image_name
                tag = "latest"

            # Tạo URL API để kiểm tra image
            url = f"https://hub.docker.com/v2/repositories/{repo_name}/tags/{tag}/"

            headers = {}
            if token:
                headers['Authorization'] = f'Bearer {token}'

            # Gửi yêu cầu GET để kiểm tra sự tồn tại của image
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                return True
            elif response.status_code == 404:
                return False
            else:
                response.raise_for_status()  

        def check_hugging_face_exists(model_id, model_token=None, check_dockerfile=False, is_config=False):
            # Tạo URL API để kiểm tra image
            url = f"https://huggingface.co/api/models/{model_id}"

            headers = {}
            if model_token:
                headers['Authorization'] = f'Bearer {model_token}'

            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    status = file_exists_in_hf_repo(model_id, check_dockerfile=check_dockerfile, is_config=is_config)
                    return status
                elif response.status_code == 404:
                    return False
                else:
                    response.raise_for_status()
            except:
                return False
    
        validate_source = True
        validate_checkpoint = True
        info_run = None

        #  HUGGING_FACE,ROBOFLOW,GIT,DOCKER_HUB,KAGGLE,CLOUD_STORAGE
        if model_source == "GIT":
            validate_source = check_git_repo_exists(model_id, model_token, True)
            info_run = read_file_content_from_repo(model_id, model_token, "Dockerfile")
        elif model_source == 'DOCKER_HUB':
            validate_source = check_docker_image_exists(request.data.get("docker_image"), request.data.get("docker_access_token"))
        elif model_source == 'HUGGING_FACE':
            validate_source = check_hugging_face_exists(model_id, model_token, True)
            info_run = read_file_content_from_hf(model_id, model_token, "Dockerfile")
        # elif model_source == 'KAGGLE':
        #     validate_source = check_kaggle_exists(model_path,model_id, model_token)
        elif model_source == "LOCAL":
            file = request.FILES.get("file")
            zip_file_content = file.read()
            if file and allowed_file(file.name):
                validate_source = check_files_in_zip(file, True)
                info_run = read_dockerfile_content_from_uploaded(zip_file_content)
            else:
                return Response(
                    {
                        "messages": "Invalid file",
                    },
                    status=400,
                )

        if not validate_source:
            return Response(
                    {
                        "messages": "The path does not exist.",
                    },
                    status=400,
                )

        # elif validate_source == '1':
        #     return Response(
        #             {
        #                 "messages": "The Dockerfile does not exist or is not at the top level of the ZIP file.",
        #             },
        #             status=400,
        #         )
        
        if checkpoint_source == "GIT":
            validate_checkpoint = check_git_repo_exists(checkpoint_id, checkpoint_token)
        elif checkpoint_source == 'HUGGING_FACE':
            if not model_source: 
                from .functions import gen_ml_hf_source

                validate_checkpoint = check_hugging_face_exists(checkpoint_id, checkpoint_token, is_config=True)
                model_source = "CHECKPOINT"
                file = gen_ml_hf_source(checkpoint_source, model_name)
                zip_file_content = file.read()
            else:
                validate_checkpoint = check_hugging_face_exists(checkpoint_id, checkpoint_token, is_config=False)
        # elif checkpoint_source == 'KAGGLE':
        #     validate_checkpoint = check_kaggle_exists(model_path,model_id, model_token)

        if not validate_checkpoint:
            return Response(
                    {
                        "messages": "The path does not exist.",
                    },
                    status=400,
                )
        elif validate_checkpoint == '2':
            return Response(
                    {
                        "messages": "There is no valid checkpoint available.",
                    },
                    status=400,
                )
        # elif validate_checkpoint == '3':
        #     return Response(
        #             {
        #                 "messages": "There is no config.json file.",
        #             },
        #             status=400,
        #         )
        # check_org_admin = OrganizationMember.objects.filter(organization_id = project.organization_id, user_id=self.request.user.id, is_admin=True).exists()
        # if not check_org_admin:
        #     if not project.organization.created_by_id == self.request.user.id and not self.request.user.is_superuser:
        #         return Response({"messages": "You do not have permission to perform this action."}, status=403)
        if project_config:
            project.epochs = int(project_config["epochs"])
            project.batch_size = int(project_config["batch_size"])
            project.steps_per_epochs = int(project_config["batch_size_per_epochs"])
            project.save()

        @transaction.atomic
        def process_compute(compute_id, index, gpus_id_list=None, model_name = None, model_pk = None, info_run=None, max_pk_network=None):

            compute = ComputeMarketplace.objects.filter(
                id=compute_id,
            ).first()

            if not compute:
                error_compute_ids.append(compute_id)
                error_messages[compute_id] = (
                    f"Compute with ID {compute_id} not found or not available for the user."
                )
                return

            try:
                if compute_id not in processed_compute_ids:
                    # gpus_index_str = None
                    # gpus_id_str = None
                    gpus_id_list = gpus_id_list.split(",")
                    if gpus_id_list:
                        # Process GPUs
                        for gpu_id in gpus_id_list:
                            compute_gpu = ComputeGPU.objects.filter(id=gpu_id).first()
                            if not compute_gpu:
                                error_compute_ids.append(compute_id)
                                error_messages[compute_id] = (
                                    f"ComputeGPU with id {gpu_id} not found"
                                )
                                return

                            # if (
                            #     project.computer_quantity_use_max
                            #     < compute_gpu.quantity_used
                            # ):
                            #     error_compute_ids.append(compute_id)
                            #     error_messages[compute_id] = (
                            #         "You have exhausted the number of model installations for the GPU"
                            #     )
                            #     return

                            # if compute_gpu.status != "renting":
                            #     error_compute_ids.append(compute_id)
                            #     error_messages[compute_id] = (
                            #         f"You cannot buy a model for computer IP {compute.ip_address} with a GPU name {compute_gpu.gpu_name} - Index {compute_gpu.gpu_index}"
                            #     )
                            #     return

                            compute_gpu.quantity_used += 1
                            compute_gpu.save()

                        gpus_index = str(ComputeGPU.objects.get(id=gpu_id).gpu_index)
                    #     gpus_index_str = ",".join(gpus_index)
                    #     gpus_id_str = ",".join(map(str, gpus_id_list))
                    # else:
                    #     gpus_index_str = None
                    #     gpus_id_str = None

                    # max_pk = ModelMarketplace.objects.aggregate(Max("pk"))["pk__max"]

                    # if not max_pk:
                    #     max_pk = 0
                    if not ModelMarketplace.objects.filter(pk=model_pk).exists():
                        _model = ModelMarketplace.objects.create(
                            pk=model_pk, # + int(index),
                            name=name,
                            model_name=model_name,
                            owner_id=user_id,
                            author_id=user_id,
                            model_desc=request.data.get("model_desc"),
                            docker_image=request.data.get("docker_image"),
                            docker_access_token=request.data.get("docker_access_token"),
                            file=request.data.get("file"),
                            infrastructure_id=compute.infrastructure_id,
                            port=compute.port,
                            ip_address=compute.ip_address,
                            config={
                                "token_length": token_length,
                                "accuracy": model_info_json["accuracy"],
                                "sampling_frequency": model_info_json["sampling_frequency"],
                                "mono": model_info_json["mono"],
                                "fps": model_info_json["fps"],
                                "resolution": model_info_json["resolution"],
                                "image_width": model_info_json["image_width"],
                                "image_height": model_info_json["image_height"],
                                "framework": model_info_json["framework"],
                                "precision": model_info_json["precision"],
                                "calculate_compute_gpu": calculate_compute_gpu,
                                "estimate_time": model_info_json["estimate_time"],
                                "estimate_cost": model_info_json["estimate_cost"],
                            },
                            model_id=model_id,
                            model_token=model_token,
                            checkpoint_id=checkpoint_id,
                            checkpoint_token=checkpoint_token,
                            checkpoint_source=checkpoint_source,
                            model_source=model_source,
                        )

                        now = datetime.now()
                        date_str = now.strftime("%Y%m%d")
                        time_str = now.strftime("%H%M%S")
                        
                        version = f'{date_str}-{time_str}'

                        history_build = History_Build_And_Deploy_Model.objects.create(
                            version = version,
                            model_id = _model.pk,
                            # checkpoint_id = checkpoint_id,
                            project_id = project_id,
                            user_id = user_id,
                            type = History_Build_And_Deploy_Model.TYPE.BUILD
                        )

                        if checkpoint_id != '':
                            checkpoint_instance = CheckpointModelMarketplace.objects.create(name=checkpoint_id, file_name=checkpoint_id, owner_id=user_id, author_id=user_id, project_id=project.id,
                                                    catalog_id=project.template.catalog_model_id if project.template.catalog_model_id else 0, model_id=0, order=0, config=checkpoint_token, checkpoint_storage_id=0, version=checkpoint_id, type=checkpoint_source)

                            ModelMarketplace.objects.filter(id=_model.pk).update(checkpoint_storage_id=checkpoint_instance.id)
                            History_Build_And_Deploy_Model.objects.filter(id=history_build.pk).update(checkpoint_id=checkpoint_instance.id)
                        
                    else:
                        _model = ModelMarketplace.objects.filter(pk=model_pk).first()
                    
                    model_name = f"{user_id}-{_model.id}-{name}"
                    # build docker images
                    # docker_image = build_model(model_source, model_id, model_token, model_name)
                    # if docker_image:
                    #     _model.docker_image = docker_image
                    #     _model.save()
                    #  handle process for model source, checkpoint
                    _port = None

                    schema = 'https'
                    if _model.schema:
                        schema = f'{_model.schema}'.replace('://', '')
                    # check ml network default

                    if not max_pk_network and max_pk_network == 0:
                        name_pk = 0
                    else:
                        name_pk = max_pk_network

                    ml_network = MLNetwork.objects.filter(
                        project_id=project_id,
                        name=f"{model_type}_{name_pk}",
                        # model_id=_model.id,
                        deleted_at__isnull=True,
                    ).first()
                    if ml_network is None:
                        ml_network = MLNetwork.objects.create(
                            project_id=project_id,
                            name=f"{model_type}_{name_pk}",
                            model_id = _model.id,
                            type = model_type
                        )
                    model_history = History_Rent_Model.objects.create(
                        model_id=_model.id,
                        model_new_id=_model.id,
                        project_id=project_id,
                        user_id=user_id,
                        model_usage=99,
                        type= History_Rent_Model.TYPE.ADD,
                        # time_end=timezone.now() + timezone.timedelta(days=365)
                        time_end= None
                    )

                    ml = MLBackend.objects.create(
                        url=f"{schema}://{compute.ip_address}:{_model.port}",
                        project_id=project_id,
                        state=MLBackendState.DISCONNECTED,  # set connected for ml install
                        install_status=MLBackend.INSTALL_STATUS.INSTALLING,
                        config=config_ml,
                        mlnetwork=ml_network,
                    )

                    ModelMarketplace.objects.filter(id=_model.pk).update(ml_id=ml.id)
                    ml_gpu = MLGPU.objects.create(
                        ml_id=ml.id,
                        model_id=_model.id,
                        gpus_index=gpus_index,
                        gpus_id=gpu_id,  # if null -> using cpu
                        compute_id=compute.id,
                        infrastructure_id=compute.infrastructure_id,
                        port=_model.port,
                        model_history_rent_id = model_history.id
                    )

                    MLNetworkHistory.objects.create(
                            ml_network=ml_network,
                            ml_id=ml.id,
                            ml_gpu_id=ml_gpu.id,
                            project_id=project_id,
                            model_id = _model.id, #model rented
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

                    thread = threading.Thread(
                        target=handle_add_model,
                        args=(
                            self,
                            compute,
                            _model,
                            project_id,
                            gpus_index,
                            gpu_id,
                            _model,
                            ml,
                            ml_gpu,
                            model_source,
                            model_id,
                            model_token,
                            model_name,
                            ml_network.id,
                            file,
                            zip_file_content,
                            info_run,
                            self.request.user
                        ),
                    )
                    thread.start()

                    processed_compute_ids.append(compute_id)

            except Exception as e:
                notify_for_compute(self.request.user.uuid, "Danger", "The model installation has failed.")
                error_compute_ids.append(compute_id)
                error_messages[compute_id] = (
                    f"Error processing compute instance: {str(e)}"
                )
                return

        max_pk = ModelMarketplace.objects.aggregate(Max("pk"))["pk__max"]
        max_pk_network = MLNetwork.objects.aggregate(Max("pk"))["pk__max"]
        if not max_pk:
            max_pk = 0

        for gpu_info in gpus_data:
            gpus = gpu_info.get("gpus_id", "").split(",")
            compute_id = gpu_info.get("compute_id")
            if MLGPU.objects.filter(compute_id=compute_id, deleted_at__isnull=True).exists() and model_source == ModelMarketplace.ModelSource.DOCKER_HUB:
                error_compute_ids.append(compute_id)
                error_messages[compute_id] = (
                    "This compute instance is running services on another project and cannot install a new image from Docker Hub."
                )
                continue

            for index, gpu_id in enumerate(gpus):
                process_compute(compute_id, index, gpu_id, model_name, max_pk+1, info_run, max_pk_network)

        # if cpus_ids and len(cpus_ids)> 0:
        #     for compute_id in cpus_ids:
        #         pass

        if processed_compute_ids:
            return Response(
                {
                    "processed_compute_ids": processed_compute_ids,
                    "error_compute_ids": error_compute_ids,
                    "messages": error_messages,
                },
                status=200,
            )
        else:
            notify_for_compute(self.request.user.uuid, "Danger", "The model installation has failed.")
            if error_compute_ids:
                return Response(
                    {
                        "error_compute_ids": error_compute_ids,
                        "messages": error_messages,
                    },
                    status=400,
                )
            else:
                return Response(
                    {
                        "error_compute_ids": "No compute",
                        "messages": "No compute is available",
                    },
                    status=400,
                )

        # else:
        #     return Response({'message': 'Your success message here'}, status=200)


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="commercialize Model Marketplace",
        operation_description="Commercialize Model Marketplace",
        manual_parameters=[
            openapi.Parameter(
                "file",
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                description="Document to be uploaded",
            ),
            openapi.Parameter(
                "name",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="name",
                required=True,
            ),
            openapi.Parameter(
                "model_desc",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="model_desc",
            ),
            openapi.Parameter(
                "ip_address",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="ip_address",
            ),
            openapi.Parameter(
                "model_id",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="model_id for model source / model url",
                required=False,
            ),
            openapi.Parameter(
                "model_token",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="model_token",
                required=False,
            ),
            openapi.Parameter(
                "checkpoint_id",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="checkpoint_id / checkpoint url",
                required=False,
            ),
            openapi.Parameter(
                "checkpoint_token",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="checkpoint_token",
                required=False,
            ),
            openapi.Parameter(
                "model_source",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="HUGGING_FACE,ROBOFLOW,GIT,DOCKER_HUB",
                required=False,
            ),
            openapi.Parameter(
                "checkpoint_source",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="HUGGING_FACE,ROBOFLOW,GIT,KAGGLE,CLOUD_STORAGE",
                required=False,
            ),
            openapi.Parameter(
                "cpus_ids",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="cpus_ids list id cpu selected - id of compute, eg:1,2,3",
            ),
            openapi.Parameter(
                "compute_id",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="compute_id",
            ),
            openapi.Parameter(
                "model_info",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="model_info",
                required=True,
                example={
                    "token_length": "4096",
                    "accuracy": "70",
                    "sampling_frequency": "48000",
                    "mono": "true",
                    "fps": "",
                    "resolution": "320",
                    "image_width": "213",
                    "image_height": "208",
                    "framework": "pytorch",
                    "precision": "fp16",
                    "project": {
                        "epochs": "1",
                        "batch_size": "1",
                        "batch_size_per_epochs": "1",
                    },
                    "calculate_compute_gpu": {
                        "paramasters": 0,
                        "mac": "0.0",
                        "gpu_memory": 548037826969,
                        "tflops": 0,
                        "time": 1,
                        "total_cost": "0.128",
                        "total_power_consumption": 0,
                        "can_rent": "false",
                        "token_symbol": "usd",
                    },
                    "rent_time": 1,
                    "rent_cost": "0.128",
                    "estimate_time": 1,
                    "estimate_cost": "0.128",
                },
            ),
            openapi.Parameter(
                "catalog_id",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="catalog_id model type",
                required=False,
            ),
            openapi.Parameter(
                "price_per_hours",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="price unit per hours",
                required=False,
            ),
            openapi.Parameter(
                "check_sequential_sampling_tasks",
                openapi.IN_FORM,
                type=openapi.TYPE_BOOLEAN,
                description="Sequential sampling Tasks are ordered by Data manager ordering",
                required=False,
            ),
            openapi.Parameter(
                "check_random_sampling",
                openapi.IN_FORM,
                type=openapi.TYPE_BOOLEAN,
                description="Random sampling. Tasks are chosen with uniform random",
                required=False,
            ),
            openapi.Parameter(
                "auto_provision",
                openapi.IN_FORM,
                type=openapi.TYPE_BOOLEAN,
                description="auto_provision",
                required=False,
            ),
            openapi.Parameter(
                "gpus",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="gpus",
                example='[{"compute_id":"25","gpus_id":"26"}]',
            ),
        ],
    ),
)
class CommercializeModelApi(APIView):
    parser_classes = (MultiPartParser, FileUploadParser)
    serializer_class = CommercializeModelSerializer
    permission_required = ViewClassPermission(
        POST=all_permissions.annotations_view,
        PATCH=all_permissions.annotations_view,
    )

    def post(self, request, *args, **kwargs):
        user_id = self.request.user.id
        gpus_data = json.loads(request.data.get("gpus", "[]"))
        cpus_ids = request.data.get("cpus_ids",[])
        model_id = request.data.get("model_id")
        name = request.data.get("name")
        model_token = request.data.get("model_token")
        checkpoint_id = request.data.get("checkpoint_id")
        checkpoint_token = request.data.get("checkpoint_token")
        model_source = request.data.get("model_source")
        checkpoint_source = request.data.get("checkpoint_source")
        model_info = request.data.get("model_info")
        model_info_json = json.loads(model_info)
        calculate_compute_gpu = model_info_json["calculate_compute_gpu"]
        token_length = model_info_json["token_length"]
        project_config = model_info_json["project"]
        check_sequential_sampling_tasks =request.data.get("check_sequential_sampling_tasks")
        check_random_sampling = request.data.get("check_random_sampling")
        price_per_hours = request.data.get("price")
        catalog_id = request.data.get("catalog_id")
        _model = None
        processed_compute_ids = []
        error_compute_ids = []
        error_messages = {}

        ALLOWED_EXTENSIONS = {'zip', 'rar', 'gz', 'tar.gz'}

        def allowed_file(filename):
            # Check if the file extension is in the allowed set
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        def check_file_extension_in_list(files, extensions=LIST_CHECKPOINT_FORMAT, is_config=False):
            # if is_config:
            #     if 'config.json' not in files:
            #         return '3'
                
            for file in files:
                ext = os.path.splitext(file)[-1]  # Lấy đuôi mở rộng của file
                if ext in extensions:
                    return True
            return '2'
        
        def list_files_in_repo(repo_url, token=None, path='', check_dockerfile=False):
            headers = {}
            if token:
                headers['Authorization'] = f'token {token}'
            
            # API endpoint to list files in a specific directory
            api_url = f"{repo_url}/contents/{path}"
            
            try:
                response = requests.get(api_url, headers=headers, allow_redirects=True)
                if response.status_code == 200:
                    contents = response.json()
                    # List all files in the specified directory
                    files = [item['path'] for item in contents if item['type'] == 'file']
                    
                    if check_dockerfile:
                        if 'Dockerfile' not in files:
                            return '1'
                    else:
                        return check_file_extension_in_list(files, is_config=True)
                    return True
            except Exception as e:
                print(e)
                return True
                    
        def file_exists_in_hf_repo(model_name, token=None, path='', check_dockerfile=False, is_config=False):
            # API URL to list files in the model repository
            api_url = f"https://huggingface.co/api/models/{model_name}/tree/main"
            
            try:
                response = requests.get(api_url, allow_redirects=True)
                if response.status_code == 200:
                    contents = response.json()
                    # Check if the file_path exists in the list of files
                    files = [item['path'] for item in contents if item['type'] == 'file']
                    if check_dockerfile:
                        if 'Dockerfile' not in files:
                            return '1'
                    else:
                        return check_file_extension_in_list(files, is_config=is_config)
                    return True
            except Exception as e:
                print(e)
                return True

        def check_files_in_zip(file, check_dockerfile=False):
            try:
                with zipfile.ZipFile(file, 'r') as zip_ref:
                    zip_file_list = zip_ref.namelist()
                    if check_dockerfile: 
                        # if not any(file_path.endswith('Dockerfile') for file_path in zip_file_list):
                        if not any(file_path == "Dockerfile" for file_path in zip_file_list):
                            return '1'
                    else:
                        for zip_file in zip_file_list:
                            ext = os.path.splitext(zip_file)[-1].lower()
                            if ext in LIST_CHECKPOINT_FORMAT:
                                return True
                        return '2'
                            
                    return True
            except zipfile.BadZipFile:
                return False
        
        def check_grpc_usage_in_file(repo_url, token=None, file_name=None):
            import base64
            if not file_name:
                return False, 
            contains_ssl = False
            headers = {}
            if token:
                headers['Authorization'] = f'token {token}'
            
            # API URL để đọc nội dung file Python
            file_api_url = f"{repo_url}/contents/{file_name}"
            
            try:
                response = requests.get(file_api_url, headers=headers)
                if response.status_code == 200:
                    content_data = response.json()
                    if content_data['type'] == 'file':
                        # Giải mã nội dung file từ Base64
                        file_content = base64.b64decode(content_data['content']).decode('utf-8')
                        ssl_patterns = [
                            r"ssl_context\s*=",  # Flask (app.run(ssl_context=...))
                            r"certfile\s*=",      # FastAPI / Uvicorn
                            r"keyfile\s*=",
                            r"ssl\.SSLContext",
                            r"ssl\.wrap_socket",
                            r"\.crt",            
                            r"\.pem"
                        ]

                        contains_ssl = any(re.search(pattern, file_content) for pattern in ssl_patterns)
                        
                        # Kiểm tra xem có sử dụng gRPC trong file không
                        if 'import grpc' in file_content or 'from grpc' in file_content:
                            return True, contains_ssl
                    return False, contains_ssl
                else:
                    print(f"Lỗi khi lấy file: {response.status_code}, {response.text}")
                    return False, contains_ssl
            except Exception as e:
                print(f"Exception occurred: {e}")
                return False, contains_ssl
        
        def check_grpc_usage_in_file_hf(repo_url, token=None, file_name=None):
            if not file_name:
                return False
            contains_ssl = False
            headers = {}
            if token:
                headers['Authorization'] = f'Bearer {token}'
            
            # API URL để đọc nội dung file Python
            file_api_url = f"{repo_url}/raw/main/{file_name}"
            
            try:
                response = requests.get(file_api_url, headers=headers)
                if response.status_code == 200:
                    file_content = response.text
                    ssl_patterns = [
                        r"ssl_context\s*=",  # Flask (app.run(ssl_context=...))
                        r"certfile\s*=",      # FastAPI / Uvicorn
                        r"keyfile\s*=",
                        r"ssl\.SSLContext",   # Sử dụng module ssl
                        r"ssl\.wrap_socket",
                        r"\.crt",             # File chứng chỉ
                        r"\.pem"
                    ]

                    contains_ssl = any(re.search(pattern, file_content) for pattern in ssl_patterns)
                    
                    # Kiểm tra xem có sử dụng gRPC trong file không
                    if 'import grpc' in file_content or 'from grpc' in file_content:
                        return True, contains_ssl
                    
                    return False, contains_ssl
                else:
                    print(f"Lỗi khi lấy file: {response.status_code}, {response.text}")
                    return False, contains_ssl
            except Exception as e:
                print(f"Exception occurred: {e}")
                return False, contains_ssl

        def check_grpc_usage_in_uploaded_file(zip_file_content, file_name=None):
            import io
            if not file_name:
                return False
            
            contains_ssl = False
            try:
                with zipfile.ZipFile(io.BytesIO(zip_file_content), 'r') as zip_ref:
                    # Đảm bảo rằng file tồn tại trong ZIP
                    if file_name in zip_ref.namelist():
                        with zip_ref.open(file_name) as file:
                            file_content = file.read().decode('utf-8')
                            ssl_patterns = [
                                r"ssl_context\s*=",  # Flask (app.run(ssl_context=...))
                                r"certfile\s*=",      # FastAPI / Uvicorn
                                r"keyfile\s*=",
                                r"ssl\.SSLContext",   # Sử dụng module ssl
                                r"ssl\.wrap_socket",
                                r"\.crt",             # File chứng chỉ
                                r"\.pem"
                            ]

                            contains_ssl = any(re.search(pattern, file_content) for pattern in ssl_patterns)

                            # Kiểm tra xem có sử dụng gRPC trong file không
                            if 'import grpc' in file_content or 'from grpc' in file_content:
                                return True, contains_ssl
                            
                return False, contains_ssl
            except Exception as e:
                print(f"Exception occurred: {e}")
                return False, contains_ssl
        
        def read_dockerfile_content_from_uploaded(zip_file_content):
            import io
            import re
            try:
                with zipfile.ZipFile(io.BytesIO(zip_file_content), 'r') as zip_ref:
                    # Kiểm tra sự tồn tại của Dockerfile trong ZIP
                    dockerfile_content = None
                    for file_name in zip_ref.namelist():
                        if 'Dockerfile' in file_name:
                            with zip_ref.open(file_name) as file:
                                dockerfile_content = file.read().decode('utf-8')
                                break

                    if not dockerfile_content:
                        return {
                            'run_command': "Không tìm thấy Dockerfile trong file ZIP.",
                            'exposed_ports': [],
                            'grpc_used': False
                        }

                    # Tìm các lệnh CMD hoặc ENTRYPOINT
                    cmd_match = re.findall(r'^CMD\s+(.*)', dockerfile_content, re.MULTILINE)
                    entrypoint_match = re.findall(r'^ENTRYPOINT\s+(.*)', dockerfile_content, re.MULTILINE)

                    # Gộp tất cả lệnh CMD và ENTRYPOINT
                    commands = cmd_match + entrypoint_match
                    run_command = None

                    # Lọc và xử lý để trả về chính xác lệnh chạy
                    for command in commands:
                        # Loại bỏ CMD/ENTRYPOINT và các ký tự không cần thiết như [], " hoặc '
                        cleaned_command = re.sub(r'^\[|\]$', '', command).strip()
                        cleaned_command = cleaned_command.replace('"', '').replace("'", "")

                        # Nếu lệnh chứa dấu phẩy, kết hợp lại thành chuỗi
                        if ',' in cleaned_command:
                            cleaned_command = ' '.join(cleaned_command.split(','))

                        # Chỉ lấy phần lệnh chạy chính (bỏ exec nếu có)
                        if cleaned_command.startswith("exec "):
                            cleaned_command = cleaned_command[5:].strip()

                        # Trả về lệnh nếu nó có chứa python hoặc gunicorn
                        if "python" in cleaned_command or "gunicorn" in cleaned_command:
                            run_command = cleaned_command
                            break

                    # Kiểm tra các cổng expose trong Dockerfile
                    exposed_ports = re.findall(r'EXPOSE\s+([0-9\s]+)', dockerfile_content)
    
                    # Tách tất cả các cổng ra từ chuỗi, và loại bỏ khoảng trắng
                    ports_list = exposed_ports[0].split() if exposed_ports else []

                    grpc_used = False
                    if run_command and "python" in run_command:
                        # Lấy tên file Python thực thi từ lệnh chạy (ví dụ: "python app.py")
                        python_file = re.findall(r'python(?:\d+(?:\.\d+)*)?\s+(\S+)', run_command)
                        if python_file:
                            grpc_used, ssl_used = check_grpc_usage_in_uploaded_file(zip_file_content, python_file[0])

                    # Trả về kết quả với lệnh chạy và các cổng expose
                    return {
                        'run_command': run_command if run_command else None,
                        'exposed_ports': ports_list if ports_list else None,
                        'grpc_used': grpc_used
                    }

            except Exception as e:
                print(f"Exception occurred: {e}")
                return {
                    'run_command': "Lỗi khi đọc Dockerfile trong file ZIP.",
                    'exposed_ports': [],
                    'grpc_used': False
                }
            
        def read_file_content_from_hf(model_id, token=None, file_path=''):
            import re
            headers = {}
            repo_url = f"https://huggingface.co/{model_id}"
            
            if token:
                headers['Authorization'] = f'Bearer {token}'
            
            # API endpoint để lấy nội dung file
            api_url = f"{repo_url}/resolve/main/{file_path}"
            
            try:
                response = requests.get(api_url, headers=headers)
                if response.status_code == 200:
                    file_content = response.text
                    
                    # Tìm các lệnh CMD hoặc ENTRYPOINT (trong trường hợp là Dockerfile)
                    cmd_match = re.findall(r'^CMD\s+(.*)', file_content, re.MULTILINE)
                    entrypoint_match = re.findall(r'^ENTRYPOINT\s+(.*)', file_content, re.MULTILINE)
                    
                    # Gộp tất cả lệnh CMD và ENTRYPOINT
                    commands = cmd_match + entrypoint_match
                    run_command = None
                    
                    # Lọc và xử lý để trả về chính xác lệnh chạy
                    for command in commands:
                        # Loại bỏ CMD/ENTRYPOINT và các ký tự không cần thiết như [], " hoặc '
                        cleaned_command = re.sub(r'^\[|\]$', '', command).strip()
                        cleaned_command = cleaned_command.replace('"', '').replace("'", "")

                        # Nếu lệnh chứa dấu phẩy, kết hợp lại thành chuỗi
                        if ',' in cleaned_command:
                            cleaned_command = ' '.join(cleaned_command.split(','))

                        # Chỉ lấy phần lệnh chạy chính (bỏ exec nếu có)
                        if cleaned_command.startswith("exec "):
                            cleaned_command = cleaned_command[5:].strip()

                        # Trả về lệnh nếu nó có chứa python hoặc gunicorn
                        if "python" in cleaned_command or "gunicorn" in cleaned_command:
                            run_command = cleaned_command
                            break
                    
                    exposed_ports = re.findall(r'EXPOSE\s+([0-9\s]+)', file_content)
    
                    # Tách tất cả các cổng ra từ chuỗi, và loại bỏ khoảng trắng
                    ports_list = exposed_ports[0].split() if exposed_ports else []


                    grpc_used = False
                    if run_command and "python" in run_command:
                        # Lấy tên file Python thực thi từ lệnh chạy (ví dụ: "python app.py")
                        python_file = re.findall(r'python(?:\d+(?:\.\d+)*)?\s+(\S+)', run_command)
                        if python_file:
                            grpc_used, ssl_used = check_grpc_usage_in_file_hf(repo_url, token, python_file[0])
                    
                    # Trả về kết quả với lệnh chạy và các cổng expose
                    return {
                        'run_command': run_command if run_command else None,
                        'exposed_ports': ports_list if ports_list else None,
                        'grpc_used': grpc_used
                    }
                
                else:
                    print(f"Error: {response.status_code}, {response.text}")
                    return None
                
            except Exception as e:
                print(f"Exception occurred: {e}")
                return None
            
        def read_file_content_from_repo(repo_url, token=None, file_path=''):
            import base64
            import re
            headers = {}
            repo_url = repo_url.replace("https://github.com/", "https://api.github.com/repos/")
            repo_url = repo_url.removesuffix(".git")
            if token:
                headers['Authorization'] = f'token {token}'
            
            # API endpoint để lấy nội dung file
            api_url = f"{repo_url}/contents/{file_path}"
            
            try:
                response = requests.get(api_url, headers=headers)
                if response.status_code == 200:
                    content_data = response.json()
                    if content_data['type'] == 'file':
                        # Giải mã nội dung Base64
                        dockerfile_content = base64.b64decode(content_data['content']).decode('utf-8')
                        
                        # Tìm các lệnh CMD hoặc ENTRYPOINT
                        cmd_match = re.findall(r'^CMD\s+(.*)', dockerfile_content, re.MULTILINE)
                        entrypoint_match = re.findall(r'^ENTRYPOINT\s+(.*)', dockerfile_content, re.MULTILINE)
                        
                        # Gộp tất cả lệnh CMD và ENTRYPOINT
                        commands = cmd_match + entrypoint_match
                        run_command = None
                        
                        # Lọc và xử lý để trả về chính xác lệnh chạy
                        for command in commands:
                            # Loại bỏ CMD/ENTRYPOINT và các ký tự không cần thiết như [], " hoặc '
                            cleaned_command = re.sub(r'^\[|\]$', '', command).strip()
                            cleaned_command = cleaned_command.replace('"', '').replace("'", "")

                            # Nếu lệnh chứa dấu phẩy, kết hợp lại thành chuỗi
                            if ',' in cleaned_command:
                                cleaned_command = ' '.join(cleaned_command.split(','))

                            # Chỉ lấy phần lệnh chạy chính (bỏ exec nếu có)
                            if cleaned_command.startswith("exec "):
                                cleaned_command = cleaned_command[5:].strip()

                            # Trả về lệnh nếu nó có chứa python hoặc gunicorn
                            if "python" in cleaned_command or "gunicorn" in cleaned_command:
                                run_command = cleaned_command
                                break
                        
                         # Tìm các cổng expose trong Dockerfile
                        exposed_ports = re.findall(r'^(?!#)\s*EXPOSE\s+([0-9\s]+)', dockerfile_content, re.MULTILINE)
    
                        # Tách tất cả các cổng ra từ chuỗi, và loại bỏ khoảng trắng
                        ports_list = exposed_ports[0].split() if exposed_ports else []

                        grpc_used = False
                        if run_command and "python" in run_command:
                            # Lấy tên file Python thực thi từ lệnh chạy (ví dụ: "python app.py")
                            python_file = re.findall(r'python(?:\d+(?:\.\d+)*)?\s+(\S+)', run_command)
                            if python_file:
                                grpc_used, ssl_used = check_grpc_usage_in_file(repo_url, token, python_file[0])
                        
                        
                        # Trả về kết quả với lệnh chạy và các cổng expose
                        return {
                            'run_command': run_command if run_command else None,
                            'exposed_ports': ports_list if ports_list else None,
                            'grpc_used': grpc_used
                        }
                            
                else:
                    print(f"Error: {response.status_code}, {response.text}")
                    return None
                
            except Exception as e:
                print(f"Exception occurred: {e}")
                return None
         
        file = request.data.get("file")
        zip_file_content = None
        # project = Project.objects.get(pk=int(project_id))

        def check_git_repo_exists(repo_url, token=None, check_dockerfile=False):
            headers = {}
            repo_url = repo_url.replace("https://github.com/", "https://api.github.com/repos/")
            repo_url = repo_url.removesuffix(".git")

            if token:
                headers['Authorization'] = f'token {token}'

            try:
                response = requests.get(repo_url, headers=headers, allow_redirects=True)
                if response.status_code == 200: 
                    status = list_files_in_repo(repo_url, token, check_dockerfile=check_dockerfile)
                    return status
                elif response.status_code == 404:
                    return False
                else:
                    # return True
                    response.raise_for_status()

            except Exception as e:
                print(e)
                return False

        def check_docker_image_exists(image_name, token=None):
            # Tách tên repo và tag từ image_name
            if ':' in image_name:
                repo_name, tag = image_name.split(':')
            else:
                repo_name = image_name
                tag = "latest"

            # Tạo URL API để kiểm tra image
            url = f"https://hub.docker.com/v2/repositories/{repo_name}/tags/{tag}/"

            headers = {}
            if token:
                headers['Authorization'] = f'Bearer {token}'

            # Gửi yêu cầu GET để kiểm tra sự tồn tại của image
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                return True
            elif response.status_code == 404:
                return False
            else:
                response.raise_for_status()  

        def check_hugging_face_exists(model_id, model_token=None, check_dockerfile=False, is_config=False):
            # Tạo URL API để kiểm tra image
            url = f"https://huggingface.co/api/models/{model_id}"

            headers = {}
            if model_token:
                headers['Authorization'] = f'Bearer {model_token}'

            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    status = file_exists_in_hf_repo(model_id, check_dockerfile=check_dockerfile, is_config=is_config)
                    return status
                elif response.status_code == 404:
                    return False
                else:
                    response.raise_for_status()
            except:
                return False
    
        validate_source = True
        validate_checkpoint = True
        info_run = None

        #  HUGGING_FACE,ROBOFLOW,GIT,DOCKER_HUB,KAGGLE,CLOUD_STORAGE
        if model_source == "GIT":
            validate_source = check_git_repo_exists(model_id, model_token, True)
            info_run = read_file_content_from_repo(model_id, model_token, "Dockerfile")
        elif model_source == 'DOCKER_HUB':
            validate_source = check_docker_image_exists(request.data.get("docker_image"), request.data.get("docker_access_token"))
        elif model_source == 'HUGGING_FACE':
            validate_source = check_hugging_face_exists(model_id, model_token, True)
            info_run = read_file_content_from_hf(model_id, model_token, "Dockerfile")
        # elif model_source == 'KAGGLE':
        #     validate_source = check_kaggle_exists(model_path,model_id, model_token)
        elif model_source == "LOCAL":
            file = request.FILES.get("file")
            zip_file_content = file.read()
            if file and allowed_file(file.name):
                validate_source = check_files_in_zip(file, True)
                info_run = read_dockerfile_content_from_uploaded(zip_file_content)
            else:
                return Response(
                    {
                        "messages": "Invalid file",
                    },
                    status=400,
                )

        if not validate_source:
            return Response(
                    {
                        "messages": "The path does not exist.",
                    },
                    status=400,
                )

        # elif validate_source == '1':
        #     return Response(
        #             {
        #                 "messages": "The Dockerfile does not exist or is not at the top level of the ZIP file.",
        #             },
        #             status=400,
        #         )
        
        if checkpoint_source == "GIT":
            validate_checkpoint = check_git_repo_exists(checkpoint_id, checkpoint_token)
        elif checkpoint_source == 'HUGGING_FACE':
            if not model_source: 
                from .functions import gen_ml_hf_source

                validate_checkpoint = check_hugging_face_exists(checkpoint_id, checkpoint_token, is_config=True)
                model_source = "CHECKPOINT"
                file = gen_ml_hf_source(checkpoint_source, name)
                zip_file_content = file.read()
            else:
                validate_checkpoint = check_hugging_face_exists(checkpoint_id, checkpoint_token, is_config=False)
        # elif checkpoint_source == 'KAGGLE':
        #     validate_checkpoint = check_kaggle_exists(model_path,model_id, model_token)

        if not validate_checkpoint:
            return Response(
                    {
                        "messages": "The path does not exist.",
                    },
                    status=400,
                )
        elif validate_checkpoint == '2':
            return Response(
                    {
                        "messages": "There is no valid checkpoint available.",
                    },
                    status=400,
            )

        @transaction.atomic
        def process_compute(compute_id, index, gpus_id_list=None):

            compute = ComputeMarketplace.objects.filter(
                id=compute_id,
            ).first()

            if not compute:
                error_compute_ids.append(compute_id)
                error_messages[compute_id] = (
                    f"Compute with ID {compute_id} not found or not available for the user."
                )
                return

            try:
                if compute_id not in processed_compute_ids:
                    gpus_index_str = None
                    gpus_id_str = None
                    if gpus_id_list:
                        # Process GPUs
                        for gpu_id in gpus_id_list:
                            compute_gpu = ComputeGPU.objects.filter(id=gpu_id).first()
                            if not compute_gpu:
                                error_compute_ids.append(compute_id)
                                error_messages[compute_id] = (
                                    f"ComputeGPU with id {gpu_id} not found"
                                )
                                return

                            compute_gpu.quantity_used += 1
                            compute_gpu.save()

                        gpus_index = str(ComputeGPU.objects.get(id=gpu_id).gpu_index)
                        gpus_index_str = ",".join(gpus_index)
                        gpus_id_str = ",".join(map(str, gpus_id_list))
                    else:
                        gpus_index_str = None
                        gpus_id_str = None

                    max_pk = ModelMarketplace.objects.aggregate(Max("pk"))["pk__max"]

                    # copy model from model rent
                    # update model config = model_config
                    _model = ModelMarketplace.objects.create(
                        pk=max_pk + 1 + int(index),
                        name=request.data.get("name"),
                        owner_id=user_id,
                        author_id=user_id,
                        model_desc=request.data.get("model_desc"),
                        docker_image=request.data.get("docker_image"),
                        docker_access_token=request.data.get("docker_access_token"),
                        file=request.data.get("file"),
                        infrastructure_id=compute.infrastructure_id,
                        port=compute.port,
                        ip_address=compute.ip_address,
                        config={
                            "token_length": token_length,
                            "accuracy": model_info_json["accuracy"],
                            "sampling_frequency": model_info_json["sampling_frequency"],
                            "mono": model_info_json["mono"],
                            "fps": model_info_json["fps"],
                            "resolution": model_info_json["resolution"],
                            "image_width": model_info_json["image_width"],
                            "image_height": model_info_json["image_height"],
                            "framework": model_info_json["framework"],
                            "precision": model_info_json["precision"],
                            "calculate_compute_gpu": calculate_compute_gpu,
                            "estimate_time": model_info_json["estimate_time"],
                            "estimate_cost": model_info_json["estimate_cost"],
                        },
                        model_id=model_id,
                        model_token=model_token,
                        checkpoint_id=checkpoint_id,
                        checkpoint_token=checkpoint_token,
                        checkpoint_source=checkpoint_source,
                        model_source=model_source,
                        price=price_per_hours,
                        catalog_id = catalog_id,
                        status= "in_marketplace"
                    )
                    # run demo
                    # create project demo for all user
                    project = Project.objects.filter(title='demo').first()
                    if project is None:
                        project = Project.objects.create(
                            title="demo", created_by_id=1, organization_id=1, is_draft =True
                        )
                    model_name = f"{user_id}-{_model.id}-{name}"

                    _port = None
                    schema = None
                    if _model.schema:
                        schema = f"{_model.schema}".replace("://", "")
                    
                    ml = MLBackend.objects.create(
                        url=f"{schema}://{compute.ip_address}:{_model.port}",
                        project_id=project.id,  # demo using project id = 0
                        state=MLBackendState.DISCONNECTED,  # set connected for ml install
                        install_status=MLBackend.INSTALL_STATUS.INSTALLING,
                    )

                    ModelMarketplace.objects.filter(id=_model.pk).update(ml_id=ml.id)
                    ml_gpu = MLGPU.objects.create(
                        ml_id=ml.id,
                        model_id=_model.id,
                        gpus_index=gpus_index,
                        gpus_id=gpu_id,  # if null -> using cpu
                        compute_id=compute.id,
                        infrastructure_id=compute.infrastructure_id,
                        port=_model.port,
                    )

                    ml_backend_status = MLBackendStatus.objects.create(
                        ml_id=ml.id,
                        project_id=project.id,  # demo using 0
                        status=MLBackendStatus.Status.WORKER,
                        status_training=MLBackendStatus.Status.JOIN_MASTER,
                        type_training=MLBackendStatus.TypeTraining.AUTO,
                    )

                    # # build docker images
                    # docker_image = build_model(
                    #     model_source, model_id_url, model_token, model_name
                    # )
                    # if docker_image:
                    #     _model.docker_image = docker_image
                    #     _model.save()

                    thread = threading.Thread(
                        target=handle_add_model,
                        args=(
                            self,
                            compute,
                            _model,
                            project.id,
                            gpus_index,
                            gpu_id,
                            _model,
                            ml,
                            ml_gpu,
                            model_source,
                            model_id,
                            model_token,
                            model_name,
                        ),
                    )
                    thread.start()

                    processed_compute_ids.append(compute_id)

            except Exception as e:
                error_compute_ids.append(compute_id)
                error_messages[compute_id] = (
                    f"Error processing compute instance: {str(e)}"
                )
                return

        for gpu_info in gpus_data:
            gpus = gpu_info.get("gpus_id", "").split(",")
            compute_id = gpu_info.get("compute_id")
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=len(gpus)
            ) as executor:
                futures = []
                for index, gpu_id in enumerate(gpus):
                    gpu_ids = gpu_id.split(",")
                    future = executor.submit(process_compute, compute_id, index, gpu_ids)
                    futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                except Exception as e:
                    print(f"An error occurred: {e}")

        for compute_id in cpus_ids:
            process_compute(compute_id)
        
        if len(cpus_ids) == 0 and len(gpus_data) == 0:
            max_pk = ModelMarketplace.objects.aggregate(Max("pk"))["pk__max"]

            _model = ModelMarketplace.objects.create(
                pk=max_pk + 1,
                name=request.data.get("name"),
                owner_id=user_id,
                author_id=user_id,
                model_desc=request.data.get("model_desc"),
                docker_image=request.data.get("docker_image"),
                docker_access_token=request.data.get("docker_access_token"),
                file=request.data.get("file"),
                infrastructure_id=None,
                port=None,
                ip_address=None,
                config={
                    "token_length": token_length,
                    "accuracy": model_info_json["accuracy"],
                    "sampling_frequency": model_info_json["sampling_frequency"],
                    "mono": model_info_json["mono"],
                    "fps": model_info_json["fps"],
                    "resolution": model_info_json["resolution"],
                    "image_width": model_info_json["image_width"],
                    "image_height": model_info_json["image_height"],
                    "framework": model_info_json["framework"],
                    "precision": model_info_json["precision"],
                    "calculate_compute_gpu": calculate_compute_gpu,
                    "estimate_time": model_info_json["estimate_time"],
                    "estimate_cost": model_info_json["estimate_cost"],
                },
                model_id=model_id,
                model_token=model_token,
                checkpoint_id=checkpoint_id,
                checkpoint_token=checkpoint_token,
                checkpoint_source=checkpoint_source,
                model_source=model_source,
                price=price_per_hours,
                status = "in_marketplace",
                catalog_id = catalog_id
            )
        # run auto select master, join master
        # auto_ml_nodes(project.id) when demo ml disable
        # if error_compute_ids:
        if processed_compute_ids:
            return Response(
                {
                    "processed_compute_ids": processed_compute_ids,
                    "error_compute_ids": error_compute_ids,
                    "messages": error_messages,
                    "id": _model.pk if _model else 0,
                },
                status=200,
            )
        else:
            if error_compute_ids:
                return Response(
                    {
                        "error_compute_ids": error_compute_ids,
                        "messages": error_messages,
                    },
                    status=400,
                )
            else:
                return Response(
                    {
                        "messages": "Commercialize Model Successfully",
                        "id": _model.pk if _model else 0,
                    },
                    status=200,
                )


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Get List Catalog Model Marketplace Paginate",
        operation_description="Get List Catalog Model Marketplace Paginate.",
    ),
)
class CataLogModelMarketplacePaginateAPI(generics.ListAPIView):
    serializer_class = CatalogModelMarketplaceSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.annotations_view,
    )
    pagination_class = SetPagination

    def get_queryset(self):
        return CatalogModelMarketplace.objects.order_by("-id")

    def get(self, request, *args, **kwargs):
        return super(CataLogModelMarketplacePaginateAPI, self).get(
            request, *args, **kwargs
        )


@method_decorator(
    name="patch",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Update Catalog Model Marketplace",
        operation_description="Update Catalog Model Marketplace.",
    ),
)
class CataLogModelMarketplaceUpdateAPI(generics.UpdateAPIView):
    serializer_class = CatalogModelMarketplaceSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.annotations_change,
    )
    redirect_kwarg = "pk"
    queryset = CatalogModelMarketplace.objects.all()

    def patch(self, request, *args, **kwargs):
        return super(CataLogModelMarketplaceUpdateAPI, self).patch(
            request, *args, **kwargs
        )

    @swagger_auto_schema(auto_schema=None)
    def put(self, request, *args, **kwargs):
        return super(CataLogModelMarketplaceUpdateAPI, self).put(
            request, *args, **kwargs
        )


@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Delete Catalog Model Marketplace",
        operation_description="Delete Catalog Model Marketplace.",
    ),
)
class CataLogModelMarketplaceDelAPI(generics.DestroyAPIView):
    serializer_class = CatalogModelMarketplaceSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.annotations_view,
    )

    def get_queryset(self):
        return CatalogModelMarketplace.objects.order_by("-id")

    def delete(self, request, *args, **kwargs):
        super(CataLogModelMarketplaceDelAPI, self).delete(request, *args, **kwargs)
        return Response({"status": "success"}, status=200)


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Create Catalog Model Marketplace",
        operation_description="Create Catalog Model Marketplace.",
    ),
)
class CataLogModelMarketplaceCreateAPI(generics.CreateAPIView):
    serializer_class = CatalogModelMarketplaceSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.annotations_create,
    )
    queryset = CatalogModelMarketplace.objects.all()

    def post(self, request, *args, **kwargs):
        return super(CataLogModelMarketplaceCreateAPI, self).post(
            request, *args, **kwargs
        )


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Check available model",
        operation_description="""Check available model""",
    ),
)
@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Check available model",
        operation_description="""Check available model""",
    ),
)
class CheckModelAvailableAPI(generics.RetrieveAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    serializer_class = HistoryRentModelSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.annotations_view,
        POST=all_permissions.annotations_view,
    )

    def get(self, request, model_id, *args, **kwargs):
        model_id = self.kwargs.get("model_id")

        model_using = History_Rent_Model.objects.filter(
            user_id=request.user.id, model_id=model_id, status="renting"
        ).first()

        is_rent_model = True
        model_usage = 0
        time_available = 0
        print("model_using", model_using)

        if model_using:
            model_using.check_status()
            model_usage = model_using.model_usage

            if model_using.status == "renting":
                time_start = model_using.time_start
                time_end = model_using.time_end
                time_available = (time_end - time_start).total_seconds() / 3600
                if time_available > 0:
                    is_rent_model = False
        return Response(
            {
                "is_rent_model": is_rent_model,
                "model_usage": model_usage,
                "time_available": time_available,
            },
            status=200,
        )

    def post(self, request, *args, **kwargs):
        pass


@method_decorator(
    name="patch",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Patch Install Model Marketplace",
        operation_description={
            "author_id": 1,
            "gpus": [
                {"compute_id": 5, "gpus_id": "10,11"},
                {"compute_id": 3, "gpus_id": "9"},
            ],
            "cpus": [{"compute_id": 6}],
            "project_id": 2,
        },
        request_body=UpdateMarketplaceSerializer,
    ),
)
class InstallModelMarketplaceByIdAPI(generics.UpdateAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    serializer_class = UpdateMarketplaceSerializer
    permission_required = ViewClassPermission(
        PATCH=all_permissions.model_marketplace_change,
    )
    lookup_field = "pk"

    def get_queryset(self):
        return ModelMarketplace.objects.all()

    @swagger_auto_schema(auto_schema=None)
    def put(self, request, *args, **kwargs):
        return super(UpdateModelMarketplaceByIdAPI, self).put(request, *args, **kwargs)

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        model = ModelMarketplace.objects.filter(
            id=self.kwargs["pk"]
        ).first()  # model rent
        user_id = self.request.user.id
        history_model_rent = History_Rent_Model.objects.filter(
            model_id=model.id, user_id=user_id, status="renting"
        ).first()
        if history_model_rent is None:
            Response(
                {"detail": "You do not own this model. Please rent the model."},
                status=400,
            )
        try:
            print("history_model_rent", history_model_rent)
            project_config = self.request.data.get("project")
            config_model = self.request.data.get("config")
            calculate_compute_gpu = self.request.data.get("calculate_compute_gpu")
            # estimate_cost = self.request.data.get('estimate_cost')
            # estimate_time = self.request.data.get('estimate_time')

            project_id = self.request.data.get("project_id")
            project = Project.objects.get(pk=project_id)

            if project_config:
                project.epochs = int(project_config["epochs"])
                project.batch_size = int(project_config["batch_size"])
                project.steps_per_epochs = int(project_config["batch_size_per_epochs"])
                project.save()

            gpus_data = self.request.data.get("gpus", [])
            cpus_data = self.request.data.get("cpus", [])
            processed_compute_ids = []
            error_compute_ids = []
            error_messages = {}
            ml_network = None
            def process_compute(compute_id, gpu_id=None, max_pk=None):
                compute = ComputeMarketplace.objects.filter(
                    id=compute_id,
                ).first()
                if not compute:
                    error_compute_ids.append(compute_id)
                    error_messages[compute_id] = (
                        f"Compute with ID {compute_id} not found or not available for the user."
                    )
                    return

                try:
                    if compute_id not in processed_compute_ids:
                        gpus_index_str = None
                        gpus_id_str = None
                        # Process GPUs
                        compute_gpu = ComputeGPU.objects.filter(id=gpu_id).first()
                        if not compute_gpu:
                            error_compute_ids.append(compute_id)
                            error_messages[compute_id] = (
                                f"ComputeGPU with id {gpu_id} not found"
                            )
                            return

                        # if (
                        #     project.computer_quantity_use_max
                        #     < compute_gpu.quantity_used
                        # ):
                        #     error_compute_ids.append(compute_id)
                        #     error_messages[compute_id] = (
                        #         "You have exhausted the number of model installations for the GPU"
                        #     )
                        #     return

                        # if compute_gpu.status != "renting":
                        #     error_compute_ids.append(compute_id)
                        #     error_messages[compute_id] = (
                        #         f"You cannot buy a model for computer IP {compute.ip_address} with a GPU name {compute_gpu.gpu_name} - Index {compute_gpu.gpu_index}"
                        #     )
                        #     return

                        compute_gpu.quantity_used += 1
                        compute_gpu.save()

                        gpus_index = str(ComputeGPU.objects.get(id=gpu_id).gpu_index)

                        # max_pk = ModelMarketplace.objects.aggregate(Max("pk"))[
                        #     "pk__max"
                        # ]
                        if not ModelMarketplace.objects.filter(pk=max_pk).exists():
                            _model = ModelMarketplace.objects.create(
                                pk=max_pk,
                                name=model.name,
                                owner_id=model.owner_id,
                                author_id=self.request.user.id,
                                model_desc=model.model_desc,
                                docker_image=model.docker_image,
                                docker_access_token=model.docker_access_token,
                                file=model.file,
                                infrastructure_id=compute.infrastructure_id,
                                ip_address=compute.ip_address,
                                port=model.port,
                                config=(
                                    json.dumps(config_model)
                                    if config_model
                                    else json.dumps(model.config)
                                ),
                                model_id=model.model_id,
                                model_token=model.model_token,
                                checkpoint_id=model.checkpoint_id,
                                checkpoint_token=model.checkpoint_token,
                                checkpoint_source=model.checkpoint_source,
                                model_source=model.model_source,
                            )

                            now = datetime.now()
                            date_str = now.strftime("%Y%m%d")
                            time_str = now.strftime("%H%M%S")
                            
                            version = f'{date_str}-{time_str}'

                            history_build = History_Build_And_Deploy_Model.objects.create(
                                version = version,
                                model_id = _model.pk,
                                # checkpoint_id = checkpoint_id,
                                project_id = project_id,
                                user_id = user_id,
                                type = History_Build_And_Deploy_Model.TYPE.BUILD
                            )
                            _model.save()
                        else:
                            _model = ModelMarketplace.objects.filter(pk=max_pk).first()

                        ## install model  turn off send mail

                        # html_file_path =  './templates/mail/rent_model_sucess.html'
                        # with open(html_file_path, 'r', encoding='utf-8') as file:
                        #     html_content = file.read()

                        # data = {
                        #     "subject": "Welcome to AIxBlock - Registration Successful!",
                        #     "from": "noreply@aixblock.io",
                        #     "to": [f'{self.request.user.email}'],
                        #     "html": html_content,
                        #     "text": "Welcome to AIxBlock!",
                        #     "attachments": []
                        # }

                        # docket_api = "tcp://69.197.168.145:4243"
                        # host_name = '69.197.168.145'

                        # email_thread = threading.Thread(target=send_email_thread, args=(docket_api, host_name, data,))
                        # email_thread.start()

                        # check ml network
                        _port = None
                        ml_network = MLNetwork.objects.filter(project_id=project_id,model_id=_model.id, deleted_at__isnull = True).first()
                        if ml_network is None:
                            # create ml network
                            ml_network = MLNetwork.objects.create(
                                project_id=project_id,
                                name=_model.name, 
                                model_id = _model.id
                            )

                        ml = MLBackend.objects.create(
                            url=f"http://{compute.ip_address}:{_model.port}",
                            project_id=project_id,
                            state=MLBackendState.DISCONNECTED,  # set connected for ml install
                            install_status=MLBackend.INSTALL_STATUS.INSTALLING,
                            mlnetwork=ml_network,
                        )

                        ModelMarketplace.objects.filter(id=_model.pk).update(
                            ml_id=ml.id
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
                            model_id = _model.id, #model rented
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
                        processed_compute_ids.append(compute_id)
                        return

                except Exception as e:
                    print(e)
                    error_compute_ids.append(compute_id)
                    error_messages[compute_id] = (
                        f"Error processing compute instance: {str(e)}"
                    )
                    return

            max_pk = ModelMarketplace.objects.aggregate(Max("pk"))["pk__max"]

            if not max_pk:
                max_pk = 0

            for gpu_info in gpus_data:
                gpu_id = gpu_info.get("gpus_id", "")
                compute_id = gpu_info.get("compute_id")
                if MLGPU.objects.filter(compute_id=compute_id, deleted_at__isnull=True).exists() and not model.model_id:
                    error_compute_ids.append(compute_id)
                    error_messages[compute_id] = (
                        "This compute instance is running services on another project and cannot install a new image from Docker Hub."
                    )
                    continue

                process_compute(compute_id, gpu_id, max_pk+1)
                # with concurrent.futures.ThreadPoolExecutor(
                #     max_workers=len(gpus)
                # ) as executor:
                #     futures = []
                #     for gpu_id in gpus:
                #         future = executor.submit(process_compute, compute_id, gpu_id, max_pk+1)
                #         futures.append(future)

                # for future in concurrent.futures.as_completed(futures):
                #     try:
                #         result = future.result()
                #     except Exception as e:
                #         print(f"An error occurred: {e}")

            for cpu_info in cpus_data:
                compute_id = cpu_info.get("compute_id")
                process_compute(compute_id)

            # run auto select master, join master
            # if ml_network:
            #     auto_ml_nodes(self,project.id, ml_network.id)
            if processed_compute_ids:
                return Response(
                    {
                        "processed_compute_ids": processed_compute_ids,
                        "error_compute_ids": error_compute_ids,
                        "messages": error_messages,
                    },
                    status=200,
                )
            else:
                if error_compute_ids:
                    return Response(
                        {
                            "error_compute_ids": error_compute_ids,
                            "messages": error_messages,
                        },
                        status=400,
                    )
                else:
                    return Response(
                        {
                            "error_compute_ids": "No compute",
                            "messages": "No compute is available",
                        },
                        status=400,
                    )
        except Exception as e:
            print(e)
            transaction.set_rollback(True)
            return Response({"detail": str(e)}, status=500)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Get detail Download Stats",
    ),
)
class DownloadModelDataAPI(generics.RetrieveAPIView):
    serializer_class = ModelMarketplaceDownloadSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.model_marketplace_view,
    )

    def get(self, request, *args, **kwargs):
        model_id = self.kwargs["pk"]
        project_id =self.request.query_params.get('project_id')
        if project_id:
            project_instance = Project.objects.filter(id=project_id).first()

        today = timezone.now()
        first_day_of_month = today.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        last_day_of_month = first_day_of_month.replace(
            day=1, month=first_day_of_month.month
        ) - timezone.timedelta(days=1)

        download_count = ModelMarketplaceDownload.objects.filter(
            model_id=model_id,
            created_at__gte=first_day_of_month,
            created_at__lte=last_day_of_month,
        ).count()
        total_params = 0

        try:
            data_type_prj = project_instance.data_types

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

            if "image" in data_type_prj: 
                from tensorflow.keras.applications import EfficientNetB3
                import tensorflow as tf

                model = tf.keras.applications.Xception(
                    weights='imagenet',
                    input_shape=(150, 150, 3),
                    include_top=False
                ) 
                total_params = model.count_params()
                
            elif "text" in data_type_prj or 'llm' in data_type_prj or  'nlp' in data_type_prj:
                args_mem = config_cacl_mem().parse_args(["--num-gpus", f"{1}", "--num-layers", "44", "--sequence-length", f"{4096}", "--num-attention-heads", "64", "--hidden-size", "6144", "--batch-size-per-gpu", "1", "--checkpoint-activations", "--zero-stage", "1", "--partition-activations", "--pipeline-parallel-size", "1", "--tensor-parallel-size", "1"])
                total_params, _ = calc_mem(args_mem)
            

        except Exception as e:
            total_params = 0
            print(e)

        return Response({"download_count": download_count, "model_size": total_params, "tensor_type": "FP16"})

@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Users'],
    operation_summary='Build Model Source',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['model_type', 'source_url'],
        properties={
            'model_type': openapi.Schema(type=openapi.TYPE_STRING, description='model_type'),
            'source_url': openapi.Schema(type=openapi.TYPE_STRING, description='source_url'),
            'source_token': openapi.Schema(type=openapi.TYPE_STRING, description='source_token'),
            'model_name': openapi.Schema(type=openapi.TYPE_STRING, description='model_name'),
            'folder_path': openapi.Schema(type=openapi.TYPE_STRING, description='folder_path')
        },
    ),
))
class BuildModelSourceAPI(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def post(self, request, *args, **kwargs):
        from core.settings.base import HOST_JUPYTERHUB, MEDIA_ROOT
        from compute_marketplace.models import History_Rent_Computes

        folder_path = request.data.get('folder_path')
        access_token = request.headers.get('Authorization')
        token_value = access_token.split(' ')[1]
        name = request.data.get('name')
        project_id = request.data.get('project_id')
        # checkpoint_id = request.data.get("checkpoint_id")

        user_id = request.user.id

        uploaded_file = None
        checkpoint_file = None
        checkpoint_name = None

        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
        
        if 'checkpoint' in request.FILES:
            checkpoint_file = request.FILES['checkpoint']
    
            # Định nghĩa đường dẫn đích
            file_name = checkpoint_file.name  # Lấy tên file
            file_path = os.path.join(MEDIA_ROOT, 'checkpoints', file_name)  # Đường dẫn đích của file
            
            # Tạo thư mục nếu chưa tồn tại
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Lưu file vào đường dẫn đích
            with open(file_path, 'wb+') as destination:
                for chunk in checkpoint_file.chunks():
                    destination.write(chunk)
            
            # Upload file lên các storages
            from io_storages.functions import get_all_project_storage, get_all_project_storage_with_name
            storages = get_all_project_storage_with_name(project_id)
            for storage in storages:
                storage.upload_file(file_name, file_path, f'checkpoint_{project_id}')
                storage_name  = storage.storage_name
                storage_id = storage.id
                checkpoint_name = file_name
                break
        
        docker_image = ""

        if uploaded_file:
            # docker_image = "aixblock/template_ml"
            # status_code = 200
            try:
                from .functions import build_jenkin_from_zipfle
                docker_image = build_jenkin_from_zipfle(uploaded_file, None)
                status_code = 200
            except Exception as e:
                res_detail = e
                status_code = 400
        else:
            if request.user.username == "admin":
                username = "admin"
            else:
                username = request.user.email

            url = f"{HOST_JUPYTERHUB}/services/wow-ai-api/zip_folder/{username}"

            payload = json.dumps({
                "token": f'{token_value}',
                "folder_path": f"{folder_path}"
            })

            headers = {
                # 'Authorization': 'Token 1014eaa1327c4e969d9823fd177834ea',
                'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            results = response.json()

            if response.status_code != 200:
                return Response({"msg": "Faild", "detail": results['detail']}, status=404)

            res_detail = json.loads(results["response"])
            status_code = results["status_code"]
            docker_image = res_detail['images']
        
        ml_backends = MLBackend.objects.filter(project_id=project_id, deleted_at__isnull=True, is_deploy=False)

        gpus_ids = []

        if len(ml_backends) > 0:
            for ml_backend in ml_backends:
                ml_gpu = MLGPU.objects.filter(ml_id=ml_backend.id).first()
                gpus_id = ml_gpu.gpus_id
                gpus_ids.append(int(gpus_id) if gpus_id is not None and gpus_id not in gpus_ids else 0)
                ml_backend.deleted_at = timezone.now()
                ml_backend.save()

            rented_records = History_Rent_Computes.objects.filter(
                status="renting",
                compute_install="completed",
                account_id=request.user.id,
                deleted_by__isnull = True,
                deleted_at__isnull = True,
                compute_gpu_id__in=gpus_ids,
            ).values_list('compute_gpu_id', 'compute_marketplace_id')
        
        else:
            ml_gpu_subquery = (
                MLGPU.objects.filter(ml_id=OuterRef("pk"))
                .exclude(Q(deleted_at__isnull=False))
                .values("gpus_id")
            )

            ml_backends = MLBackend.objects.annotate(
                gpus_id=Subquery(ml_gpu_subquery)
            ) 

            gpus_ids = []

            for ml_backend in ml_backends:
                gpus_id = ml_backend.gpus_id
                gpus_ids.append(int(gpus_id) if gpus_id is not None and gpus_id not in gpus_ids else 0)

            rented_records = History_Rent_Computes.objects.filter(
                status="renting",
                compute_install="completed",
                account_id=request.user.id,
                deleted_by__isnull = True,
                deleted_at__isnull = True
            ).exclude(compute_gpu_id__in=gpus_ids).values_list('compute_gpu_id', 'compute_marketplace_id')

        def process_compute(compute_id, gpu_id, max_pk, max_pk_network=None):

            compute = ComputeMarketplace.objects.filter(
                id=compute_id,
            ).first()

            try:
                compute_gpu = ComputeGPU.objects.filter(id=gpu_id).first()
                if not compute_gpu:
                    return

                compute_gpu.quantity_used += 1
                compute_gpu.save()

                gpus_index = str(ComputeGPU.objects.get(id=gpu_id).gpu_index)

                model_source = 'DOCKER_HUB'
                checkpoint_source = 'CLOUD_STORAGE'

                if not ModelMarketplace.objects.filter(pk=max_pk).exists():
                    _model = ModelMarketplace.objects.create(
                        pk=max_pk,
                        name=name if name else docker_image,
                        owner_id=user_id,
                        author_id=user_id,
                        model_desc=request.data.get("model_desc"),
                        docker_image=docker_image,
                        docker_access_token=request.data.get("docker_access_token"),
                        file=request.data.get("file"),
                        infrastructure_id=compute.infrastructure_id,
                        port=compute.port,
                        ip_address=compute.ip_address,
                        config={
                        },
                        # model_id=model_id,
                        # model_token=model_token,
                        checkpoint_id='',
                        # checkpoint_token=None,
                        checkpoint_source=checkpoint_source,
                        model_source=model_source,
                    )

                    now = datetime.now()
                    date_str = now.strftime("%Y%m%d")
                    time_str = now.strftime("%H%M%S")
                    
                    version = f'{date_str}-{time_str}'

                    history_build = History_Build_And_Deploy_Model.objects.create(
                        version = version,
                        model_id = _model.pk,
                        # checkpoint_id = checkpoint_id,
                        project_id = project_id,
                        user_id = user_id,
                        type = History_Build_And_Deploy_Model.TYPE.BUILD
                    )

                else:
                    _model = ModelMarketplace.objects.filter(pk=max_pk).first()

                model_name = f"{user_id}-{_model.id}-{name}"

                _port = None

                schema = 'https'
                if _model.schema:
                    schema = f'{_model.schema}'.replace('://', '')

                # check ml network default
                # max_pk = MLNetwork.objects.aggregate(Max("pk"))["pk__max"]
                model_type = MLNetwork.TYPE_NETWORK.INFERENCE
                if not max_pk_network and max_pk_network == 0:
                    name_pk = 0
                else:
                    name_pk = max_pk_network

                ml_network = MLNetwork.objects.filter(
                    project_id=project_id,
                    name=f"{model_type}_{name_pk}",
                    # model_id=_model.id,
                    deleted_at__isnull=True,
                ).first()
                if ml_network is None:
                    ml_network = MLNetwork.objects.create(
                        project_id=project_id,
                        name=f"{model_type}_{name_pk}",
                        model_id = _model.id,
                        type = model_type
                    )

                # if ml_network is None:
                #     ml_network = MLNetwork.objects.create(
                #         project_id=project_id,
                #         name="default",
                #         model_id = _model.id,
                #         type=MLNetwork.TYPE_NETWORK.INFERENCE
                #     )
                model_history = History_Rent_Model.objects.create(
                    model_id=_model.id,
                    model_new_id=_model.id,
                    project_id=project_id,
                    user_id=user_id,
                    model_usage=99,
                    type= History_Rent_Model.TYPE.ADD,
                    # time_end=timezone.now() + timezone.timedelta(days=365)
                    time_end= None
                )
                
                ml = MLBackend.objects.create(
                    url=f"{schema}://{compute.ip_address}:{_model.port}",
                    project_id=project_id,
                    state=MLBackendState.DISCONNECTED,  # set connected for ml install
                    install_status=MLBackend.INSTALL_STATUS.INSTALLING,
                    config='[]',
                    mlnetwork=ml_network,
                )

                ModelMarketplace.objects.filter(id=_model.pk).update(ml_id=ml.id)

                ml_gpu = MLGPU.objects.create(
                    ml_id=ml.id,
                    model_id=_model.id,
                    gpus_index=gpus_index,
                    gpus_id=gpu_id,  # if null -> using cpu
                    compute_id=compute.id,
                    infrastructure_id=compute.infrastructure_id,
                    port=_model.port,
                    model_history_rent_id = model_history.id
                )

                MLNetworkHistory.objects.create(
                        ml_network=ml_network,
                        ml_id=ml.id,
                        ml_gpu_id=ml_gpu.id,
                        project_id=project_id,
                        model_id = _model.id, #model rented
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

                if checkpoint_name:
                    checkpoint_instance = CheckpointModelMarketplace.objects.create(name=checkpoint_name, file_name=checkpoint_name, owner_id=user_id, author_id=user_id, project_id=project_id, ml_id=ml.id,
                                            catalog_id=None, model_id=0, order=0, config={}, checkpoint_storage_id=storage_id, version=version, type="LOCAL", checkpoint_storage_name=storage_name)

                    ModelMarketplace.objects.filter(id=_model.pk).update(checkpoint_storage_id=checkpoint_instance.id)
                    History_Build_And_Deploy_Model.objects.filter(id=history_build.pk).update(checkpoint_id=checkpoint_instance.id)

                thread = threading.Thread(
                    target=handle_add_model,
                    args=(
                        self,
                        compute,
                        _model,
                        project_id,
                        gpus_index,
                        gpu_id,
                        _model,
                        ml,
                        ml_gpu,
                        model_source,
                        None,
                        None,
                        model_name,
                        ml_network.id
                    ),
                )
                thread.start()

                # processed_compute_ids.append(compute_id)

            except Exception as e:
                return

        max_pk = ModelMarketplace.objects.aggregate(Max("pk"))["pk__max"]
        max_pk_network = MLNetwork.objects.aggregate(Max("pk"))["pk__max"]

        if not max_pk:
            max_pk = 0

        for rented_record in rented_records:
            gpu_id, compute_id = rented_record
            process_compute(compute_id, gpu_id, max_pk+1, max_pk_network)

        if status_code != 200:
            return Response({"msg": "Faild", "detail": res_detail}, status=200)

        return Response({"detail": "Done", "images_build": docker_image}, status=200)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["Compute Marketplace"],
        operation_summary="Get List model rented, owner by project id",
        operation_description="Get List model rented, owner by project id",
        manual_parameters=[
            openapi.Parameter(
                name="project_id",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_QUERY,
                description="Project ID",
            ),
            page_parameter,
            search_parameter,
            field_search_parameter,
            sort_parameter,
            type_parameter,
            field_query_parameter,
            query_value_parameter,
        ],
    ),
)
class HistoryRentModelListView(generics.ListAPIView):
    serializer_class = HistoryRentModelListSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.annotations_view,
    )
    pagination_class = SetPagination
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        project_id = self.request.query_params.get("project_id")
        current_time = timezone.now()
        rented_records = History_Rent_Model.objects.filter(
            Q(deleted_at__isnull=True) &
            Q(status='renting') &
            (Q(type='add') | Q(type='rent', time_end__gt=current_time))
        )

        if project_id is not None:
            rented_records = rented_records.filter(project_id=project_id)
        
        rented_records = rented_records.distinct('model_new_id')

        return filterModel(self, rented_records, History_Rent_Model)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["Compute Marketplace"],
        operation_summary="Get List model rented, owner by project id",
        operation_description="Get List model rented, owner by project id",
        manual_parameters=[
            openapi.Parameter(
                name="project_id",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_QUERY,
                description="Project ID",
            ),
            page_parameter,
            search_parameter,
            field_search_parameter,
            sort_parameter,
            type_parameter,
            field_query_parameter,
            query_value_parameter,
        ],
    ),
)
class HistoryBuildModelListView(generics.ListAPIView):
    serializer_class = HistoryBuildModelListSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.annotations_view,
    )
    pagination_class = SetPagination
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        project_id = self.request.query_params.get("project_id")
        # current_time = timezone.now()
        rented_records = History_Build_And_Deploy_Model.objects.filter(
            Q(deleted_at__isnull=True) &
            Q(type=History_Build_And_Deploy_Model.TYPE.BUILD) #&
            # (Q(type='add') | Q(type='rent', time_end__gt=current_time))
        )

        if project_id is not None:
            rented_records = rented_records.filter(project_id=project_id)
        else:
            model_ids = list(map(int, History_Rent_Model.objects.filter(
                user_id=self.request.user.id, 
                status="renting"
            ).values_list("model_new_id", flat=True)))

            rented_records = rented_records.filter(Q(model_id__in = model_ids))
        
        rented_records = rented_records.order_by("-id")

        return filterModel(self, rented_records, History_Build_And_Deploy_Model)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Delete Build-Deploy Model Marketplace",
        operation_description="Delete Build-Deploy Marketplace!",
        manual_parameters=[
            openapi.Parameter(
                name="id",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_PATH,
                description="History Build Model ID",
            ),
        ],
    ),
)
class BuildAndDeployDeleteAPI(generics.DestroyAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    serializer_class = HistoryBuildModelListSerializer
    permission_required = ViewClassPermission(
        DELETE=all_permissions.model_marketplace_delete,
    )

    def delete(self, request, *args, **kwargs):
        history_id = kwargs['pk']
        history_instance = History_Build_And_Deploy_Model.objects.filter(id = history_id).first()
        if history_instance:
            history_instance.deleted_at = timezone.now()
            history_instance.save()
        # super(ModelMarketplaceDeleteAPI, self).delete(request, *args, **kwargs)
        try:
            History_Rent_Model.objects.filter(model_new_id=history_instance.model_id).update(status=History_Rent_Model.Status.COMPLETED)
            ml_gpus = MLGPU.objects.filter(model_id=history_instance.model_id)
            for ml_gpu in ml_gpus:
                if MLBackend.objects.filter(id = ml_gpu.ml_id, deleted_at__isnull=True).exists():
                    MLNetwork.objects.filter(model_id=ml_gpu.model_id).update(deleted_at=timezone.now())
                    MLBackendStatus.objects.filter(ml_id=ml_gpu.ml_id).update(deleted_at=timezone.now())
                    MLBackend.objects.filter(id=ml_gpu.ml_id).update(deleted_at=timezone.now())
                    ml_gpu.deleted_at = timezone.now()
                    ml_gpu.save()
        except Exception as e:
            print(e)

        return Response({"status": "success"}, status=200)
    
@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["Compute Marketplace"],
        operation_summary="Get List model rented, owner by project id",
        operation_description="Get List model rented, owner by project id",
        manual_parameters=[
            openapi.Parameter(
                name="project_id",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_QUERY,
                description="Project ID",
            )
        ],
    ),
)
class GetModelSourceProject(generics.ListAPIView):
    serializer_class = DockerImageSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.annotations_view,
    )
    pagination_class = SetPagination
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        project_id = self.request.query_params.get("project_id")
        # current_time = timezone.now()
        rented_records = History_Build_And_Deploy_Model.objects.filter(deleted_at__isnull=True, project_id=project_id).values_list("model_id") #type=History_Build_And_Deploy_Model.TYPE.BUILD
        # rented_records = History_Rent_Model.objects.filter(
        #     Q(deleted_at__isnull=True) &
        #     Q(status='renting') &
        #     (Q(type='add') | Q(type='rent', time_end__gt=current_time))
        # )

        # if project_id is not None:
        #     rented_records = rented_records.filter(project_id=project_id).values_list("model_id")

        model_source = ModelMarketplace.objects.filter(id__in=rented_records, docker_image__isnull=False).order_by("-id")
        return model_source #filterModel(self, rented_records, History_Rent_Model)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Deploy Model Marketplace",
        manual_parameters=[
            openapi.Parameter(
                "file",
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                description="Document to be uploaded",
            ),
            
            openapi.Parameter(
                "project_id",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="project_id",
                required=True,
            ),
            openapi.Parameter(
                "model_id",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="model_id",
                required=False,
            ),
            
            openapi.Parameter(
                "checkpoint_id",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="checkpoint_id",
                required=False,
            ),
            
            openapi.Parameter(
                "num_scale",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="",
                required=False,
            ),
            
            openapi.Parameter(
                "gpus", openapi.IN_FORM, type=openapi.TYPE_STRING, description="gpus"
            ),
        ],
        consumes=["multipart/form-data"],
    ),
)
class DeployModelAPI(APIView):
    parser_classes = (MultiPartParser, FileUploadParser)
    # serializer_class = ImportStorageSerializer
    permission_required = ViewClassPermission(
        POST=all_permissions.annotations_view,
        PATCH=all_permissions.annotations_view,
    )
    permission_classes = [IsSuperAdminOrg]

    def post(self, request, *args, **kwargs):
        from io_storages.functions import list_storage
        user_id = self.request.user.id
        project_id = request.data.get("project_id")
        model_id = request.data.get("model_id")
        checkpoint_id = request.data.get("checkpoint_id", None)
        gpus_data = json.loads(request.data.get("gpus", "[]"))
        num_scale = request.data.get("num_scale", 1)

        list_storages = list_storage()
        checkpoint_source = None
        def get_storage_by_name(name):
            return next((storage for storage in list_storages if storage['name'] == name), None)
        
        try:
            checkpoint_instance = CheckpointModelMarketplace.objects.filter(id=checkpoint_id).first()
            name_storage = checkpoint_instance.checkpoint_storage_id if checkpoint_instance.checkpoint_storage_id and checkpoint_instance.checkpoint_storage_id != '0' else 's3'
            checkpoint_source = f"{checkpoint_instance.name}_{name_storage}"
            storage = get_storage_by_name(checkpoint_instance.checkpoint_storage_name)
            storage_instance = storage['import_instance'].objects.filter(id=checkpoint_instance.checkpoint_storage_id).first()
            lst_object = storage_instance.get_iterkeys(f"checkpoint/{checkpoint_instance.version}/")
            def func_valid_checkpoint(lst_object):
                for obj in lst_object:
                    file_name = os.path.splitext(obj.key)[-1].lower()

                    if file_name in ['.zip', '.rar', '.gz', '.tar.gz']:
                        file_list = storage_instance.extract_zip(obj.key)
                        for file in file_list:
                            if os.path.splitext(file)[-1].lower() in LIST_CHECKPOINT_FORMAT:
                                return True

                        return False
                    else:
                        return file_name in LIST_CHECKPOINT_FORMAT
                    
            valid_checkpoint = func_valid_checkpoint(lst_object)

            if not valid_checkpoint:
                return Response(
                    {
                        "messages": "There is no valid checkpoint available.",
                    },
                    status=400,
                )
            
        except Exception as e:
            print(e)
            pass
            
        def process_compute(compute_id, gpu_id, model_id, num_scale=None):
            try:
                compute = ComputeMarketplace.objects.filter(
                    id=compute_id,
                ).first()
                compute_gpu = ComputeGPU.objects.filter(id=gpu_id).first()

                _model = ModelMarketplace.objects.filter(id=model_id).first()
                
                ml_gpu = MLGPU.objects.filter(compute_id=compute.id, gpus_id=compute_gpu.id, deleted_at__isnull=True).first()
                # print(MLBackend.objects.filter(id=ml_gpu.ml_id, deleted_at__isnull=True, install_status=MLBackend.INSTALL_STATUS.INSTALLING))
                if ml_gpu and MLBackend.objects.filter(id=ml_gpu.ml_id, deleted_at__isnull=True, install_status=MLBackend.INSTALL_STATUS.INSTALLING).exists():
                    return False

                now = datetime.now()
                date_str = now.strftime("%Y%m%d")
                time_str = now.strftime("%H%M%S")
                
                version = f'{date_str}-{time_str}'

                if compute.type != "MODEL-PROVIDER-VAST":
                    try:
                        from compute_marketplace.calc_info_host import DockerStats
                        from compute_marketplace.self_host import update_notify_install
                        from compute_marketplace.models import History_Rent_Computes
                        
                        docker_stats = DockerStats(f"http://{compute.ip_address}:{compute.docker_port}")
                        max_containers = docker_stats.scale_capacity()

                        if num_scale:
                            num_scale = int(num_scale)

                            if num_scale > max_containers:
                                history =  History_Rent_Computes.objects.filter(
                                        compute_marketplace_id=compute_id,
                                        deleted_at__isnull=True,
                                        # compute_install=History_Rent_Computes.InstallStatus.WAIT_VERIFY,
                                    ).order_by("-id").first()
                                
                                notify_for_compute(self.request.user.uuid, "Danger", f"Deploy Failed. Container scaling is limited to a maximum of {max_containers}")
                                update_notify_install(f"Deploy Failed. Container scaling is limited to a maximum of {max_containers}", self.request.user.id, f"Deploy Failed. Container scaling is limited to a maximum of {max_containers}", history.id, "Install Compute", "danger")
                                
                                return Response(
                                    {
                                        "messages": f"Deploy Failed. Container scaling is limited to a maximum of {max_containers}",
                                    },
                                    status=400,
                                )
                    except Exception as e:
                        print(e)

                ml_network = MLNetwork.objects.create(
                    project_id=project_id,
                    name=version,
                    model_id = _model.id
                )

                # model_history = History_Rent_Model.objects.create(
                #     model_id=_model.id,
                #     model_new_id=_model.id,
                #     project_id=project_id,
                #     user_id=user_id,
                #     model_usage=99,
                #     type= History_Rent_Model.TYPE.ADD,
                #     # time_end=timezone.now() + timezone.timedelta(days=365)
                #     time_end= None
                # )
                
                ml = MLBackend.objects.create(
                    url=f"{_model.schema}://{compute.ip_address}:{_model.port}",
                    project_id=project_id,
                    state=MLBackendState.DISCONNECTED,  # set connected for ml install
                    install_status=MLBackend.INSTALL_STATUS.INSTALLING,
                    mlnetwork=ml_network,
                    is_deploy=True
                )

                ModelMarketplace.objects.filter(id=_model.pk).update(ml_id=ml.id)
                ml_gpu = MLGPU.objects.create(
                    ml_id=ml.id,
                    model_id=_model.id,
                    gpus_index=compute_gpu.gpu_index,
                    gpus_id=gpu_id,  # if null -> using cpu
                    compute_id=compute.id,
                    infrastructure_id=compute.infrastructure_id,
                    port=_model.port,
                    # model_history_rent_id = model_history.id
                )

                MLNetworkHistory.objects.create(
                        ml_network=ml_network,
                        ml_id=ml.id,
                        ml_gpu_id=ml_gpu.id,
                        project_id=project_id,
                        model_id = _model.id, #model rented
                        status = MLNetworkHistory.Status.JOINED,
                        compute_gpu_id = compute_gpu.id,
                        checkpoint_id=checkpoint_id if checkpoint_id and checkpoint_id != "" else None
                    )
                
                History_Build_And_Deploy_Model.objects.create(
                    version = version,
                    model_id = _model.pk,
                    checkpoint_id = checkpoint_id if checkpoint_id and checkpoint_id != "" else None,
                    project_id = project_id,
                    user_id = user_id,
                    type = History_Build_And_Deploy_Model.TYPE.DEPLOY
                )
                
                ml_backend_status = MLBackendStatus.objects.create(
                    ml_id= ml.id,
                    project_id = project_id,
                    status= MLBackendStatus.Status.WORKER,
                    status_training = MLBackendStatus.Status.JOIN_MASTER,
                    type_training = MLBackendStatus.TypeTraining.AUTO
                )

                # if checkpoint_id != '':
                #     checkpoint_instance = CheckpointModelMarketplace.objects.create(name=checkpoint_id, file_name=checkpoint_id, owner_id=user_id, author_id=user_id, project_id=project.id, ml_id=ml.id,
                #                             catalog_id=project.template.catalog_model_id, model_id=0, order=0, config=checkpoint_token, checkpoint_storage_id=0, version=checkpoint_id, type=checkpoint_source)

                #     ModelMarketplace.objects.filter(id=_model.pk).update(checkpoint_storage_id=checkpoint_instance.id)

                thread = threading.Thread(
                    target=handle_deploy_model,
                    args=(
                        self,
                        compute,
                        _model,
                        project_id,
                        compute_gpu.gpu_index,
                        gpu_id,
                        _model,
                        ml,
                        ml_gpu,
                        _model.docker_image,
                        None,
                        checkpoint_source,
                        num_scale,
                        None,
                        self.request.user
                    ),
                )
                thread.start()

                return True

            except Exception as e:
                return Response(
                    {
                        "messages": "Fail",
                    },
                    status=400,
                )

        compute_failed = []
        for gpu_info in gpus_data:
            gpus = gpu_info.get("gpus_id", "").split(",")
            compute_id = gpu_info.get("compute_id")
            for _, gpu_id in enumerate(gpus):
                res = process_compute(compute_id, gpu_id, model_id, num_scale)
                if not res:
                    compute_failed.append(compute_id)
        
        if compute_failed:
            return Response(
                {
                    "message": f"Computes are currently installing ML: {', '.join(compute_failed)}. Please wait."
                },
                status=400
            )
        
        return Response(
                    {
                        "messages": "Success",
                    },
                    status=200,
                )


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace Tasks"],
        operation_description="Retrieve all tasks related to a specific ModelMarketplace.",
        responses={200: ModelTaskSerializer(many=True)}
    )
)
@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace Tasks"],
        operation_description="Add tasks to a specific ModelMarketplace.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'task_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER))
            }
        ),
        responses={200: openapi.Response(description="Tasks added successfully")}
    )
)
@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace Tasks"],
        operation_description="Remove tasks from a specific ModelMarketplace.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'task_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER))
            }
        ),
        responses={200: openapi.Response(description="Tasks removed successfully")}
    )
)
class ModelMarketplaceTasksAPI(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_required = ViewClassPermission(
        GET=all_permissions.model_marketplace_change,
        POST=all_permissions.model_marketplace_change,
        DELETE=all_permissions.model_marketplace_change,
    )

    def get(self, request, marketplace_id):
        try:
            marketplace = ModelMarketplace.objects.get(id=marketplace_id)
            tasks = marketplace.tasks.all()
            serializer = ModelTaskSerializer(tasks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ModelMarketplace.DoesNotExist:
            return Response({"detail": "ModelMarketplace not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, marketplace_id):
        try:
            marketplace = ModelMarketplace.objects.get(id=marketplace_id)
            task_ids = request.data.get('task_ids', [])
            tasks = ModelTask.objects.filter(id__in=task_ids)
            marketplace.tasks.add(*tasks)
            return Response({"detail": "Tasks added successfully"}, status=status.HTTP_200_OK)
        except ModelMarketplace.DoesNotExist:
            return Response({"detail": "ModelMarketplace not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, marketplace_id):
        try:
            marketplace = ModelMarketplace.objects.get(id=marketplace_id)
            task_ids = request.data.get('task_ids', [])
            tasks = ModelTask.objects.filter(id__in=task_ids)
            marketplace.tasks.remove(*tasks)
            return Response({"detail": "Tasks removed successfully"}, status=status.HTTP_200_OK)
        except ModelMarketplace.DoesNotExist:
            return Response({"detail": "ModelMarketplace not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace Tasks"],
        operation_description="Retrieve a list of all ModelTasks.",
        responses={200: ModelTaskSerializer(many=True)}
    )
)
@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace Tasks"],
        operation_description="Create a new ModelTask.",
        request_body=ModelTaskSerializer,
        responses={201: ModelTaskSerializer()}
    )
)
class ModelTaskListCreateAPI(generics.ListCreateAPIView):
    queryset = ModelTask.objects.all()
    serializer_class = ModelTaskSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.model_marketplace_create,
        POST=all_permissions.model_marketplace_create,
    )

@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace Tasks"],
        operation_description="Retrieve a specific ModelTask by ID.",
        responses={200: ModelTaskSerializer()}
    )
)
@method_decorator(
    name="put",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace Tasks"],
        operation_description="Update a specific ModelTask by ID.",
        request_body=ModelTaskSerializer,
        responses={200: ModelTaskSerializer()}
    )
)
@method_decorator(
    name="patch",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace Tasks"],
        operation_description="Partially update a specific ModelTask by ID.",
        request_body=ModelTaskSerializer,
        responses={200: ModelTaskSerializer()}
    )
)
@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace Tasks"],
        operation_description="Delete a specific ModelTask by ID.",
        responses={204: "No Content"}
    )
)
class ModelTaskDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = ModelTask.objects.all()
    serializer_class = ModelTaskSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.model_marketplace_create,
        PUT=all_permissions.model_marketplace_create,
        PATCH=all_permissions.model_marketplace_create,
        DELETE=all_permissions.model_marketplace_create,
    )
    lookup_field = 'pk'


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Calc model hf",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'model_name': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
    ),
)
class CalcHfModel(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        model_name = request.data.get("model_name", [])
        try:
            model_hf = get_model(model_name, "auto", "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")
            data = calculate_memory(model_hf, "float16")
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(e)
            return Response({"message": e.__str__()}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)