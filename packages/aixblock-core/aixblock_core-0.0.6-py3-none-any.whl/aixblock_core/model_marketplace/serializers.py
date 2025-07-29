from .models import CatalogModelMarketplace, CheckpointModelMarketplace, ModelTask
from .models import DatasetModelMarketplace, ModelMarketplace, ModelMarketplaceLike, ModelMarketplaceDownload, History_Rent_Model, History_Build_And_Deploy_Model
from rest_flex_fields import FlexFieldsModelSerializer
from users.serializers import UserSimpleSerializer
from rest_framework import serializers
from django.utils import timezone
import django_filters
from django.db.models import Q


class ModelTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelTask
        fields = '__all__'


class ModelMarketplaceSerializer(serializers.ModelSerializer):
    total_user_rent = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    download_count = serializers.SerializerMethodField()
    user_liked = serializers.SerializerMethodField()
    related_compute = serializers.SerializerMethodField()
    related_compute_gpu = serializers.SerializerMethodField()
    weights = serializers.SerializerMethodField()
    tasks = ModelTaskSerializer(many=True, read_only=True)

    def get_queryset(self):
        queryset = super().get_queryset()
        task_names = self.request.query_params.getlist('task_names', [])
        if task_names:
            queryset = queryset.filter(tasks__name__in=task_names).distinct()
        return queryset

    def get_weights(self, instance):
        import json 
        try:
            import ast
            # Thử parse bằng JSON trước
            try:
                config = json.loads(instance.config)  # Nếu chuỗi là JSON hợp lệ, parse luôn
            except json.JSONDecodeError:
                # Nếu lỗi, thử dùng ast.literal_eval()
                config = ast.literal_eval(instance.config)
            weights = config["weights"]
            return weights
        except Exception as e:
            print(f"Lỗi parsing config: {e}")
            weights = []
        
        return weights
        # return [
        #     {
        #         "name": "Weight 1",
        #         "value": "repo/model-1",
        #         "size": 11111,
        #         "paramasters": 22222,
        #         "tflops": 3333,
        #     },
        #     {
        #         "name": "Weight 2",
        #         "value": "repo/model-2",
        #         "size": 11111,
        #         "paramasters": 22222,
        #         "tflops": 3333,
        #     },
        # ]

    def get_like_count(self, instance):
        return ModelMarketplaceLike.objects.filter(model_id=instance.id).count()

    def get_download_count(self, instance):
        return ModelMarketplaceDownload.objects.filter(model_id=instance.id).count()

    def get_user_liked(self, instance):
        user_id = self.context.get('user_id')
        if not user_id:
            return False
        return ModelMarketplaceLike.objects.filter(model_id=instance.id, user_id=user_id).exists()

    def get_related_compute(self, instance):
        from ml.models import MLGPU
        from compute_marketplace.models import ComputeMarketplace

        mlgpus = MLGPU.objects.filter(model_id=instance.id, deleted_at__isnull = True).first()
        if mlgpus:
            compute =  ComputeMarketplace.objects.filter(
                    id=mlgpus.compute_id, deleted_at__isnull=True
                ).values().first()
            return compute
        return 

    def get_total_user_rent(self, instance):
        from model_marketplace.models import History_Rent_Model
        from django.contrib.auth.models import AnonymousUser
        request = self.context.get('request')
        user_id = None
        if request and not isinstance(request.user, AnonymousUser):
            user_id = request.user.id
        # Filter the History_Rent_Model records by model_id and count the unique user_id
        total_user_rent = (
            History_Rent_Model.objects.filter(
                model_id=instance.id, deleted_at__isnull=True
            )
            .exclude(user_id=user_id)
            .values("user_id")
            .distinct()
            .count()
        )

        return total_user_rent

    def get_related_compute_gpu(self, instance):
        from ml.models import MLGPU
        from compute_marketplace.models import ComputeGPU

        mlgpus = MLGPU.objects.filter(
            model_id=instance.id, deleted_at__isnull=True
        ).first()
        if mlgpus:
            compute_gpus = (
                ComputeGPU.objects.filter(id=mlgpus.gpus_id, deleted_at__isnull=True)
                .values()
                .first()
            )
            return compute_gpus
        return

    class Meta:
        model = ModelMarketplace
        fields = '__all__'
        extra_fields = ["related_compute"]


class UpdateMarketplaceSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True)
    owner_id = serializers.IntegerField(required=False)
    author_id = serializers.IntegerField(required=False)
    checkpoint_storage_id = serializers.CharField(required=False, allow_blank=True)
    ml_id = serializers.IntegerField(required=False, allow_null=True)
    catalog_id = serializers.IntegerField(required=False, allow_null=True)
    order = serializers.IntegerField(required=False, allow_null=True)
    config= serializers.JSONField(required=False)
    dataset_storage_id = serializers.IntegerField(required=False, allow_null=True)
    image_dockerhub_id = serializers.CharField(required=False, allow_blank=True)
    infrastructure_id = serializers.CharField(required=False, allow_blank=True)
    model_desc = serializers.CharField(required=False, allow_blank=True)
    type = serializers.CharField(required=False, allow_blank=True)
    ip_address = serializers.CharField(required=False, allow_blank=True)
    port = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(
        choices=[
            'created', 'in_marketplace', 'rented_bought',
            'completed', 'pending', 'suppend', 'expired'
        ],
        required=False
    )
    file = serializers.FileField(allow_empty_file=True,use_url=True, required=False)
    is_buy_least = serializers.BooleanField(required=False, default=False)
    docker_image = serializers.CharField(required=False, allow_blank=True)
    docker_access_token = serializers.CharField(required=False, allow_blank=True)
    checkpoint_id = serializers.IntegerField(required=False, allow_null=True)
    compute_gpus = serializers.JSONField(required=False)
    is_auto_update_version = serializers.BooleanField(required=False)
    interactive_preannotations = serializers.BooleanField(required=False)
    price = serializers.FloatField(required=False)

    def update(self, instance, validated_data):
        try:
            instance.name = validated_data.get('name', instance.name)
            instance.updated_at = validated_data.get('updated_at', instance.updated_at)
            instance.owner_id = validated_data.get('owner_id', instance.owner_id)
            instance.author_id = validated_data.get('author_id', instance.author_id)
            instance.checkpoint_storage_id = validated_data.get('checkpoint_storage_id', instance.checkpoint_storage_id)
            instance.ml_id = validated_data.get('ml_id', instance.ml_id)
            instance.catalog_id = validated_data.get('catalog_id', instance.catalog_id)
            instance.order = validated_data.get('order', instance.order)
            instance.config = validated_data.get('config',instance.config)
            instance.dataset_storage_id = validated_data.get('dataset_storage_id', instance.dataset_storage_id)
            instance.image_dockerhub_id = validated_data.get('image_dockerhub_id', instance.image_dockerhub_id)
            instance.infrastructure_id = validated_data.get('infrastructure_id', instance.infrastructure_id)
            instance.model_desc = validated_data.get('model_desc', instance.model_desc)
            instance.type = validated_data.get('type', instance.type)
            instance.ip_address = validated_data.get('ip_address', instance.ip_address)
            instance.port = validated_data.get('port', instance.port)
            instance.status = validated_data.get('status', instance.status)
            instance.file = validated_data.get('file', instance.file)
            instance.docker_image = validated_data.get('docker_image', instance.docker_image)
            instance.checkpoint_id = validated_data.get('checkpoint_id', instance.checkpoint_id)
            instance.compute_gpus = validated_data.get('compute_gpus', instance.compute_gpus)
            instance.is_auto_update_version = validated_data.get('is_auto_update_version', instance.is_auto_update_version)
            instance.interactive_preannotations = validated_data.get('interactive_preannotations', instance.interactive_preannotations)
            instance.price = validated_data.get('price', instance.price)
            instance.save()
        except Exception as e:
            print(e)

        return instance

class ModelMarketplaceBuySerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True)
    owner_id = serializers.IntegerField(required=False)
    author_id = serializers.IntegerField(required=False)
    catalog_id = serializers.IntegerField(required=False)
    config= serializers.CharField(required=False, allow_blank=True)
    infrastructure_id = serializers.CharField(required=False, allow_blank=True)
    model_desc = serializers.CharField(required=False, allow_blank=True)
    type = serializers.CharField(required=False, allow_blank=True)
    ip_address = serializers.CharField(required=False, allow_blank=True)
    
    def create(self, validated_data):
        validated_data['ml_id'] = 0
        validated_data['order'] = 0
        validated_data['checkpoint_storage_id'] = ''
        validated_data['dataset_storage_id'] = 0
        validated_data['image_dockerhub_id'] = ''
        validated_data['port'] = ''
        validated_data['file'] = ''
        
        return ModelMarketplace.objects.create(**validated_data)

class CatalogModelMarketplaceSerializer(FlexFieldsModelSerializer):
    filter = serializers.ChoiceField(
        required=False, allow_blank=True, allow_null=True,
        choices=[
            'name', 'tag', 'status', 'all'
        ],
    )
    keyword = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = CatalogModelMarketplace
        fields = '__all__'

class CheckpointModelMarketplaceSerializer(FlexFieldsModelSerializer):

    class Meta:
        model = CheckpointModelMarketplace
        fields = '__all__'

class DatasetModelMarketplaceSerializer(FlexFieldsModelSerializer):

    class Meta:
        model = DatasetModelMarketplace
        fields = '__all__'

class ModelMarketplaceLikeSerializer(serializers.Serializer):
    is_like = serializers.BooleanField()
    like_count = serializers.IntegerField()

class ModelMarketplaceDownloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelMarketplaceDownload
        fields = '__all__'

class AddModelSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, allow_blank=False)
    docker_image = serializers.CharField(required=True, allow_blank=False)
    docker_access_token = serializers.CharField(required=True, allow_blank=False)
    model_desc = serializers.CharField(required=False)
    file = serializers.FileField(required=False)
    ip_address = serializers.CharField(required=True, allow_blank=False)
    port = serializers.CharField(required=True, allow_blank=False)
    project_id = serializers.IntegerField(required=True)
    gpus_index = serializers.CharField(required=True, allow_blank=False)
    compute_id = serializers.IntegerField(required=True)

class CommercializeModelSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, allow_blank=False)
    docker_image = serializers.CharField(required=True, allow_blank=False)
    docker_access_token = serializers.CharField(required=True, allow_blank=False)
    model_desc = serializers.CharField(required=False)
    file = serializers.FileField(required=False)
    ip_address = serializers.CharField(required=True, allow_blank=False)
    port = serializers.CharField(required=True, allow_blank=False)
    project_id = serializers.IntegerField(required=True)
    gpus_index = serializers.CharField(required=True, allow_blank=False)
    compute_id = serializers.IntegerField(required=True)

class ModelMarketFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.CharFilter(lookup_expr='icontains')
    catalog_id = django_filters.NumberFilter()
    all = django_filters.CharFilter(method='filter_all')

    class Meta:
        model = ModelMarketplace
        fields = ['name', 'status', 'catalog_id', 'all']
    
    def filter_all(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(name__icontains=value) |
                Q(status__icontains=value)
            )
        return queryset

class ModelCheckpointUploadSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    file = serializers.FileField()

class ModelCheckpointDownloadSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()

class ModelDatasetUploadSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    file = serializers.FileField()

class ModelDatasetDownloadSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()

class HistoryRentModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = History_Rent_Model
        fields = '__all__'


class HistoryRentModelListSerializer(serializers.ModelSerializer):
    model_marketplace = serializers.SerializerMethodField()
    class Meta:
        model = History_Rent_Model
        fields = "__all__"

    def get_model_marketplace(self, obj):
        # Extract the last ID from `model_new_id`
        model_new_id_list = obj.model_new_id.split(",")
        last_model_id = model_new_id_list[-1] if model_new_id_list else None

        if last_model_id:
            try:
                # Query the ModelMarketplace with the last ID
                marketplace_model = ModelMarketplace.objects.get(id=last_model_id)
                return ModelMarketplaceSerializer(marketplace_model).data
            except ModelMarketplace.DoesNotExist:
                return None
        return None
class ZipFileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    name = serializers.CharField(max_length=255, required=False)

class DockerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelMarketplace
        fields = ['id', 'docker_image']

class HistoryBuildModelListSerializer(serializers.ModelSerializer):
    model_marketplace = serializers.SerializerMethodField()
    class Meta:
        model = History_Build_And_Deploy_Model
        fields = "__all__"

    def get_model_marketplace(self, obj):
        # Extract the last ID from `model_new_id`
        last_model_id = obj.model_id

        if last_model_id:
            try:
                # Query the ModelMarketplace with the last ID
                marketplace_model = ModelMarketplace.objects.get(id=last_model_id)
                try:
                    import json
                    config_model = marketplace_model.config
                    cleaned_config_string = json.loads(config_model)
                    # marketplace_model.config = cleaned_config_string
                    marketplace_model.config = json.dumps(cleaned_config_string)
                    marketplace_model.save()
                except:
                    pass
                history_model = History_Rent_Model.objects.filter(model_new_id=last_model_id)
                if history_model and history_model.first().type:
                    obj.type = history_model.first().type
                else:
                    obj.type = "rent"

                return ModelMarketplaceSerializer(marketplace_model).data
            except ModelMarketplace.DoesNotExist:
                return None
        return None

class HistoryDeployModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = History_Build_And_Deploy_Model
        fields = "__all__"