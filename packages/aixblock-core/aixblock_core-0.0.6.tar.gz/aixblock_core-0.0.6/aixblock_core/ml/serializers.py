"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
from django.conf import settings
from rest_framework import serializers
from ml.models import (
    MLBackend,
    MLBackendTrainJob,
    MLBackendStatus,
    MLLogs,
    MLGPU,
    MLNetworkHistory,
    MLNetwork
)
from core.utils.io import url_is_local
from core.utils.exceptions import MLModelLocalIPError
from compute_marketplace.serializers import ComputeGPUSerializer
from compute_marketplace.models import ComputeGPU, ComputeMarketplace, History_Rent_Computes
from model_marketplace.models import History_Rent_Model, ModelMarketplace, History_Build_And_Deploy_Model
from model_marketplace.serializers import HistoryDeployModelSerializer
import json
class MLBackendSerializer(serializers.ModelSerializer):
    compute_gpu_info = ComputeGPUSerializer(read_only=True)
    def validate_url(self, value):
        if settings.ML_BLOCK_LOCAL_IP and url_is_local(value):
            raise MLModelLocalIPError
        return value

    def validate(self, attrs):
        attrs = super(MLBackendSerializer, self).validate(attrs)
        url = attrs['url']
        # # ==================
        # # disable check health
        healthcheck_response = MLBackend.healthcheck_(url)
        # if healthcheck_response.is_error:
        #     raise serializers.ValidationError(
        #         f"Can't connect to ML backend {url}, health check failed. "
        #         f'Make sure it is up and your firewall is properly configured. '
        #         f'Additional info:' + healthcheck_response.error_message
        #     )
        # # ==================
        project = attrs['project']
        setup_response = MLBackend.setup_(url, project)
        # if setup_response.is_error:
        #     raise serializers.ValidationError(
        #         f"Successfully connected to {url} but it doesn't look like a valid ML backend. "
        #         f'Reason: {setup_response.error_message}.\n'
        #         f'Check the ML backend server console logs to check the status. There might be\n'
        #         f'something wrong with your model or it might be incompatible with the current labeling configuration.'
        #     )
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        schema = "https"
        ml_status_data, _ = MLBackendStatus.objects.get_or_create(
            ml_id=instance.id, project_id=instance.project_id, deleted_at__isnull=True
        )
        data["status"] = ml_status_data.status
        data["status_training"] = ml_status_data.status_training

        ml_gpu = MLGPU.objects.filter(
            ml_id=instance.id, deleted_at__isnull=True
        ).first()
        serialized_compute_gpu = {}
        if ml_gpu is not None:
            compute_gpu = ComputeGPU.objects.filter(
                id=ml_gpu.gpus_id, deleted_at__isnull=True
            ).first()
            compute_gpu_serializer = ComputeGPUSerializer(compute_gpu)
            serialized_compute_gpu = compute_gpu_serializer.data
            if compute_gpu:
                compute_marketplace = ComputeMarketplace.objects.filter(
                    id=compute_gpu.compute_marketplace_id, deleted_at__isnull=True
                ).first()
                if compute_marketplace:
                    serialized_compute_gpu["ip_address"] = (
                        compute_marketplace.ip_address
                    )
                    compute_history = History_Rent_Computes.objects.filter(
                        compute_gpu_id=compute_gpu.id, deleted_at__isnull=True
                    ).first()
                    if isinstance(compute_marketplace.config, dict):
                        config = compute_marketplace.config
                    else:
                        config = json.loads(compute_marketplace.config)
                    serialized_compute_gpu["cpu"] = config.get("cpu")
                    serialized_compute_gpu["model_port"] = ml_gpu.port
                    if compute_history:
                        serialized_compute_gpu["service_type"] = (
                            compute_history.service_type
                        )

            history_model = History_Rent_Model.objects.filter(
                id=ml_gpu.model_history_rent_id, deleted_at__isnull=True
            ).first()
            if history_model:
                model = ModelMarketplace.objects.filter(
                    id=history_model.model_id
                ).first()
                if model:
                    serialized_compute_gpu["image"] = model.docker_image
                    schema = model.schema
                    try:
                        data["model_checkpoint"] = json.loads(model.config)["weights"][0]["value"]
                    except:
                        data["model_checkpoint"] = ""
                    

        # Add the serialized ComputeGPU data to the response
        data["compute_gpu"] = serialized_compute_gpu

        # Fetch and serialize MLNetworkHistory data
        ml_network_history = MLNetworkHistory.objects.filter(
            ml_id=instance.id, deleted_at__isnull=True
        )
        serialized_network_history = MLNetworkHistorySerializer(
            ml_network_history, many=True
        ).data
        if len(serialized_network_history) > 0:
            data["network_history"] = serialized_network_history[0]
        else:
            data["network_history"] = serialized_network_history
            
        try:
            from projects.function import convert_url
            if schema == "https":
                data['url'] = "https://"+convert_url(data['url'], True)
            else:
                data['url'] = "https://"+convert_url(data['url'], False)
        except Exception as e:
            print(e)
            
        return data

    class Meta:
        model = MLBackend
        fields = '__all__'


class MLInteractiveAnnotatingRequest(serializers.Serializer):
    task = serializers.IntegerField(
        help_text='ID of task to annotate',
        required=True,
    )
    context = serializers.JSONField(
        help_text='Context for ML model',
        allow_null=True,
        default=None,
    )
# class MLBackendQueueRequest(serializers.Serializer):
#     project_id = serializers.IntegerField(
#         help_text='ID of project',
#         required=True,
#     )
#     task_id = serializers.IntegerField(
#         help_text='ID of task ',
#         required=True,
#     )
#     user_id = serializers.IntegerField(
#         help_text='ID of user',
#         required=True,
#     )
#     try_count = serializers.IntegerField(
#         help_text='try count',
#         required=False,
#     )
#     max_tries = serializers.IntegerField(
#         help_text='max tries',
#         required=False,
#     )
#     priority = serializers.IntegerField(
#         help_text='priority',
#         required=False,
#     )
#     status = serializers.CharField(
#         help_text='status',
#         required=False,
#     )

class MLBackendAdminViewSerializer(serializers.ModelSerializer):
    project = serializers.SlugRelatedField(read_only=True,slug_field='title')
    class Meta:
        model = MLBackend
        fields = '__all__'

class MLBackendTrainJobAdminViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLBackendTrainJob
        fields = '__all__'

class MLBackendStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLBackendStatus
        fields = ['ml_id', 'status', 'status_training']

class MLLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLLogs
        fields = '__all__'


class ConfigEntrySerializer(serializers.Serializer):
    entry_file = serializers.CharField(max_length=255)
    arguments = serializers.DictField(child=serializers.CharField())
    type = serializers.ChoiceField(choices=["train", "predict", "dashboard"])


class MLUpdateConfigSerializer(serializers.ModelSerializer):

    config = serializers.ListSerializer(child=ConfigEntrySerializer())
    class Meta:
        model = MLBackend
        fields = ['config']


class MLNetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLNetwork
        fields = "__all__"


class MLNetworkHistorySerializer(serializers.ModelSerializer):
    ml_network = MLNetworkSerializer(read_only=True)

    class Meta:
        model = MLNetworkHistory
        fields = "__all__"

class HistoryDeploySerializer(serializers.ModelSerializer):
    compute_gpu_info = ComputeGPUSerializer(read_only=True)
    def validate_url(self, value):
        if settings.ML_BLOCK_LOCAL_IP and url_is_local(value):
            raise MLModelLocalIPError
        return value

    def validate(self, attrs):
        attrs = super(MLBackendSerializer, self).validate(attrs)
        url = attrs['url']
        # # ==================
        # # disable check health
        healthcheck_response = MLBackend.healthcheck_(url)
        project = attrs['project']
        setup_response = MLBackend.setup_(url, project)

        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # ml_status_data, _ = MLBackendStatus.objects.get_or_create(
        #     ml_id=instance.id, project_id=instance.project_id, deleted_at__isnull=True
        # )
        # data["status"] = ml_status_data.status
        # data["status_training"] = ml_status_data.status_training

        ml_gpu = MLGPU.objects.filter(
            ml_id=instance.id, #deleted_at__isnull=True
        ).first()
        serialized_compute_gpu = {}
        data["compute_gpu"] = {}
        data["deploy_history"] = {}

        compute_gpu = ComputeGPU.objects.filter(
            id=ml_gpu.gpus_id, deleted_at__isnull=True
        ).first()
        compute_gpu_serializer = ComputeGPUSerializer(compute_gpu)
        serialized_compute_gpu = compute_gpu_serializer.data

        if compute_gpu:
            compute_marketplace = ComputeMarketplace.objects.filter(
                id=compute_gpu.compute_marketplace_id, deleted_at__isnull=True
            ).first()
            if compute_marketplace:
                serialized_compute_gpu["ip_address"] = (
                    compute_marketplace.ip_address
                )
                compute_history = History_Rent_Computes.objects.filter(
                    compute_gpu_id=compute_gpu.id, deleted_at__isnull=True
                ).first()
                if isinstance(compute_marketplace.config, dict):
                    config = compute_marketplace.config
                else:
                    config = json.loads(compute_marketplace.config)
                serialized_compute_gpu["cpu"] = config.get("cpu")
                serialized_compute_gpu["model_port"] = ml_gpu.port
                if compute_history:
                    serialized_compute_gpu["service_type"] = (
                        compute_history.service_type
                    )

                history_model = History_Rent_Model.objects.filter(
                    id=ml_gpu.model_history_rent_id, deleted_at__isnull=True
                ).first()
                if history_model:
                    model = ModelMarketplace.objects.filter(
                        id=history_model.model_id
                    ).first()
                    if model:
                        serialized_compute_gpu["image"] = model.docker_image

                # Add the serialized ComputeGPU data to the response
                data["compute_gpu"] = serialized_compute_gpu

        # Fetch and serialize MLNetworkHistory data
        # ml_network_history = MLNetworkHistory.objects.filter(
        #     ml_id=instance.id, deleted_at__isnull=True
        # )
        
        deploy_history = History_Build_And_Deploy_Model.objects.filter(project_id = instance.project_id, model_id=ml_gpu.model_id, type=History_Build_And_Deploy_Model.TYPE.DEPLOY, deleted_at__isnull=True)
        serialized_deploy_history = HistoryDeployModelSerializer(
            deploy_history, many=True
        ).data
        # serialized_network_history = MLNetworkHistorySerializer(
        #     ml_network_history, many=True
        # ).data
        if len(serialized_deploy_history) > 0:
            data["deploy_history"] = serialized_deploy_history[0]
        else:
            data["deploy_history"] = serialized_deploy_history
        
        try:
            new_deploy = self.instance.first().id
            if new_deploy == instance.id:
                from projects.function import convert_url
                data["url"] = "https://"+convert_url(instance.url, True)
        except Exception as e:
            print(e)

        return data

    class Meta:
        model = MLBackend
        fields = '__all__'