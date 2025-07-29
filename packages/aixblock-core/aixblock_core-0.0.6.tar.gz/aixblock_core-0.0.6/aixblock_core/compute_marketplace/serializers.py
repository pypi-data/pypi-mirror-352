from .models import ComputeMarketplace, CatalogComputeMarketplace, ComputeTimeWorking, ComputeGPU, Trade, ComputeGpuPrice, ComputeLogs, History_Rent_Computes, Computes_Preference, Recommend_Price
from rest_flex_fields import FlexFieldsModelSerializer
from users.serializers import UserSimpleSerializer
from rest_framework import serializers
from model_marketplace.models import ModelMarketplace 
from datetime import datetime, time
import json
import django_filters
from django.db.models import Q
from django.utils import timezone
from django import forms

class ComputeGpuPriceSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = ComputeGpuPrice
        fields = '__all__'


class ComputeLogsSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = ComputeLogs
        fields = '__all__'

class ComputeGpuRelateSerializer(FlexFieldsModelSerializer):
    prices = ComputeGpuPriceSerializer(many=True, read_only=True)
    class Meta:
        model = ComputeGPU
        fields = '__all__'

class ComputeMarketplaceSerializer(FlexFieldsModelSerializer):
    created_by = UserSimpleSerializer(default=None, help_text='ComputeMarketplace creator')
    sortField = serializers.CharField(required=False,  allow_null=True)
    compute_gpus = serializers.SerializerMethodField()
    cpu_price = serializers.SerializerMethodField(allow_null=True, read_only=True)
    time_working = serializers.SerializerMethodField(allow_null=True, read_only=True)
    remaining = serializers.SerializerMethodField(allow_null=True, read_only=True)
    currently_rented = serializers.SerializerMethodField(
        allow_null=True, read_only=True
    )
    class Meta:
        model = ComputeMarketplace
        fields = '__all__'
        widgets = {
            'username': forms.HiddenInput(),
            'password': forms.HiddenInput(),
        }

    def get_compute_gpus(self, obj):
        filtered_gpus = obj.compute_gpus.filter(deleted_at__isnull=True).exclude(
            status="been_removed"
        )

        gpu_data = ComputeGpuRelateSerializer(filtered_gpus, many=True).data

        for gpu in gpu_data:
            gpu_id = gpu["id"]
            being_rented = History_Rent_Computes.objects.filter(
                compute_gpu_id=gpu_id, status=History_Rent_Computes.Status.RENTING, deleted_at__isnull = True
            ).exists()
            gpu["being_rented"] = being_rented

        return gpu_data

    def get_cpu_price(self, obj):
        cpu_price_obj = ComputeGpuPrice.objects.filter(compute_marketplace_id=obj.id, type='cpu').first()
        if cpu_price_obj:
            return {
                'id': cpu_price_obj.id,
                'token_symbol': cpu_price_obj.token_symbol,
                'price': cpu_price_obj.price,
                'unit': cpu_price_obj.unit,
                'type': cpu_price_obj.type,
                'compute_marketplace_id': cpu_price_obj.compute_marketplace_id.id
            }
        return None

    def get_time_working(self, obj):
        time_working_objs = ComputeTimeWorking.objects.filter(
            compute_id=obj.id, deleted_at__isnull=True
        )
        time_working_data = []
        for time_working_obj in time_working_objs:
            time_working_data.append(
                {
                    "id": time_working_obj.id,
                    "compute_id": time_working_obj.compute_id,
                    "infrastructure_id": time_working_obj.infrastructure_id,
                    "time_start": time_working_obj.time_start,
                    "time_end": time_working_obj.time_end,
                    "day_range": time_working_obj.day_range,
                }
            )
        return time_working_data

    def get_remaining(self, obj):
        time_working_objs = ComputeTimeWorking.objects.filter(
            compute_id=obj.id, deleted_at__isnull=True
        )
        time_working_data = []
        for time_working_obj in time_working_objs:
            time_working_data.append(
                {
                    "id": time_working_obj.id,
                    "compute_id": time_working_obj.compute_id,
                    "infrastructure_id": time_working_obj.infrastructure_id,
                    "time_start": time_working_obj.time_start,
                    "time_end": time_working_obj.time_end,
                    "day_range": time_working_obj.day_range,
                }
            )
        total_remaining_days = 0
        previous_end_day = timezone.now()

        for record in time_working_data:
            for range_item in record.get("day_range", []):
                start_date = datetime.strptime(range_item['start_day'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
                end_date = datetime.strptime(range_item['end_day'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)

                if start_date > previous_end_day:
                    total_remaining_days += (start_date - previous_end_day).days

                if end_date > previous_end_day:
                    total_remaining_days += (end_date - max(start_date, previous_end_day)).days

                previous_end_day = max(previous_end_day, end_date)
        return str(total_remaining_days)

    def get_currently_rented(self, obj):
        history = (
            History_Rent_Computes.objects.filter(
                compute_marketplace_id=obj.id,
                deleted_at__isnull=True,
                status=History_Rent_Computes.Status.RENTING,
            )
            .exclude(type=History_Rent_Computes.Type.OWN_NOT_LEASING)
            .exists()
        )
        if history:
            return True
        return False


class HistoryRentComputesSerializer(serializers.ModelSerializer):
    class Meta:
        model = History_Rent_Computes
        fields = "__all__"

    def to_representation(self, instance):
        if instance.status == "renting" and instance.account_id == self.context['user_id']:
            return super().to_representation(instance)
        return None


class ComputeMarketplaceRentedSerializer(FlexFieldsModelSerializer):

    sortField = serializers.CharField(required=False, allow_null=True)
    compute_gpus = ComputeGpuRelateSerializer(
        many=True, allow_null=True, read_only=True
    )
    cpu_price = serializers.SerializerMethodField(allow_null=True, read_only=True)
    history_rent_computes = HistoryRentComputesSerializer(
        many=True, allow_null=True, read_only=True
    )
    time_working = serializers.SerializerMethodField(allow_null=True, read_only=True)  

    class Meta:
        model = ComputeMarketplace
        fields = "__all__"

    def get_cpu_price(self, obj):
        cpu_price_obj = ComputeGpuPrice.objects.filter(
            compute_marketplace_id=obj.id, type="cpu"
        ).first()
        if cpu_price_obj:
            return {
                "id": cpu_price_obj.id,
                "token_symbol": cpu_price_obj.token_symbol,
                "price": cpu_price_obj.price,
                "unit": cpu_price_obj.unit,
                "type": cpu_price_obj.type,
                "compute_marketplace_id": cpu_price_obj.compute_marketplace_id.id,
            }
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Remove null records from history_rent_computes list        data["history_rent_computes"] = [
        data["history_rent_computes"] = [
            record for record in data["history_rent_computes"] if record is not None
        ]
        return data

    def get_time_working(self, obj):
        time_working_objs = ComputeTimeWorking.objects.filter(compute_id=obj.id, deleted_at__isnull=True)
        time_working_data = []
        for time_working_obj in time_working_objs:
            time_working_data.append({
                "id": time_working_obj.id,
                "compute_id": time_working_obj.compute_id,
                "infrastructure_id": time_working_obj.infrastructure_id,
                "time_start": time_working_obj.time_start,
                "time_end": time_working_obj.time_end,
                "day_range": time_working_obj.day_range,
            })
        return time_working_data

class ComputeMarketplaceRentedCPUSerializer(FlexFieldsModelSerializer):
    cpu_price = serializers.SerializerMethodField(allow_null=True, read_only=True)

    class Meta:
        model = ComputeMarketplace
        fields = [
            "config",
            "id",
            "cpu_price",
            "name",
            "infrastructure_id",
            "ip_address",
            "port",
            "is_using_cpu",
            "status",
            "type",
            "compute_type",
            "owner_id",
            "location_id",
            "location_alpha2",
            "location_name",
        ]

    def get_cpu_price(self, obj):
        cpu_price_obj = ComputeGpuPrice.objects.filter(
            compute_marketplace_id=obj.id, type="cpu"
        ).first()
        if cpu_price_obj:
            return {
                "id": cpu_price_obj.id,
                "token_symbol": cpu_price_obj.token_symbol,
                "price": cpu_price_obj.price,
                "unit": cpu_price_obj.unit,
                "type": cpu_price_obj.type,
                "compute_marketplace_id": cpu_price_obj.compute_marketplace_id.id,
            }
        return None


class ComputeGPUSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComputeGPU
        fields = "__all__"


class ComputeMarketplaceRentedCardSerializer(FlexFieldsModelSerializer):
    compute_marketplace = ComputeMarketplaceRentedCPUSerializer()
    compute_gpu = ComputeGPUSerializer()
    prices = ComputeGpuPriceSerializer(read_only=True, source='compute_gpu.prices.first')  
    provider_id = serializers.SerializerMethodField()
    account_uuid = serializers.SerializerMethodField()
    new_notifications_count = serializers.SerializerMethodField()
    payment_method = serializers.SerializerMethodField()
    class Meta:
        model = History_Rent_Computes
        fields = "__all__"
    def get_provider_id(self, obj):
        return obj.compute_marketplace.owner_id
    def get_account_uuid(self, obj):
        return obj.account.uuid
    def get_new_notifications_count(self, obj):
        return obj.new_notifications.count()
    def get_payment_method(self, obj):
        try:
            trade_instance = Trade.objects.filter(order = obj.order_id, resource_id = obj.compute_gpu_id).first()
            return trade_instance.payment_method
        except Exception as e:
            return ""

class ComputeMarketplaceRentSerializer(FlexFieldsModelSerializer):
    compute_gpus_id = serializers.CharField(read_only=True)
    compute_id = serializers.IntegerField(read_only=True)
    token_name = serializers.CharField(read_only=True)
    token_symbol = serializers.CharField(read_only=True)
    amount = serializers.IntegerField(read_only=True)
    price = serializers.FloatField(read_only=True)
    # type = serializers.CharField(read_only=True)
    # status = serializers.CharField(read_only=True,)
    account = serializers.CharField(read_only=True)

    created_by = UserSimpleSerializer(default=None, help_text='ComputeMarketplace creator')
    sortField = serializers.CharField(required=False,  allow_null=True)
    compute_gpus = ComputeGpuRelateSerializer(many=True, allow_null=True, read_only=True)
    cpu_price = serializers.SerializerMethodField(allow_null=True, read_only=True)

    class Meta:
        model = ComputeMarketplace
        fields = '__all__'

    def get_cpu_price(self, obj):
        cpu_price_obj = ComputeGpuPrice.objects.filter(compute_marketplace_id=obj.id, type='cpu').first()
        if cpu_price_obj:
            return {
                'id': cpu_price_obj.id,
                'token_symbol': cpu_price_obj.token_symbol,
                'price': cpu_price_obj.price,
                'unit': cpu_price_obj.unit,
                'type': cpu_price_obj.type,
                'compute_marketplace_id': cpu_price_obj.compute_marketplace_id.id
            }
        return None


class ComputeMarketplaceUserCreateSerializer(serializers.Serializer):
    ip_address = serializers.CharField(required=True, allow_blank=False)
    client_id = serializers.CharField(required=False, allow_blank=True)
    client_secret = serializers.CharField(required=False, allow_blank=True)
    infrastructure_id = serializers.CharField(required=True, allow_blank=False)
    config = serializers.JSONField(required=True)

    def create(self, validated_data):
        user_id = validated_data['owner_id']
        org_id = validated_data['organization_id']
        current_date = datetime.now().strftime("%d%m%Y")
        name = f"{user_id}_{org_id}_{current_date}"
        validated_data['name'] = name
        config_data = validated_data.pop('config')
        return ComputeMarketplace.objects.create(config=config_data, **validated_data)

class TimeRangeSerializer(serializers.Serializer):
    start_time = serializers.CharField()
    end_time = serializers.CharField()
class ComputeMarketUserCreateFullSerializer(serializers.Serializer):
    ip_address = serializers.CharField(required=True, allow_blank=False)
    name = serializers.CharField(required=True, allow_blank=False)
    price = serializers.FloatField(required=False)
    file = serializers.FileField(required=False)
    config = serializers.JSONField(required=True)
    infrastructure_id= serializers.CharField(required=True)
    def create(self, validated_data):
        user_id = validated_data['owner_id']
        org_id = validated_data['organization_id']
        current_date = datetime.now().strftime("%d%m%Y")
        # ModelMarketplace.objects.create(
        #     name=f"{user_id}_{org_id}_{current_date}",
        #     owner_id=user_id,author_id=user_id,
        #     ip_address=validated_data['ip_address'],
        #     infrastructure_id=validated_data['infrastructure_id']
        # )
        config_data = validated_data.pop('config')
        
        # Creating ComputeMarketplace instance with config
        return ComputeMarketplace.objects.create(config=config_data, **validated_data)

class CatalogComputeMarketplaceSerializer(FlexFieldsModelSerializer):
    filter = serializers.ChoiceField(
        required=False, allow_blank=True, allow_null=True,
        choices=[
            'name', 'tag', 'status', 'all'
        ],
    )
    keyword = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = CatalogComputeMarketplace
        fields = '__all__'

class ComputeMarketFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.CharFilter(lookup_expr='icontains')
    compute_type = django_filters.CharFilter()
    catalog_id = django_filters.NumberFilter()
    all = django_filters.CharFilter(method='filter_all')

    class Meta:
        model = ComputeMarketplace
        fields = ['name', 'status', 'compute_type', 'catalog_id', 'all']
    
    def filter_all(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(name__icontains=value) |
                Q(status__icontains=value)
            )
        return queryset

class ComputeGpuSerializer(FlexFieldsModelSerializer):
    infrastructure = ComputeMarketplaceSerializer(source='infrastructure_id', read_only=True)
    power_consumption = serializers.CharField(required=False, allow_null=True, read_only=True)
    memory_usage = serializers.CharField(required=False, allow_null=True,read_only=True)
    power_usage = serializers.CharField(required=False, allow_null=True, read_only=True)
    gpu_memory = serializers.CharField(required=False, allow_null=True, read_only=True)
    class Meta:
        model = ComputeGPU
        fields = '__all__'


class ComputeMarketplaceRentSerializer(serializers.ModelSerializer):
    cpu_price = serializers.SerializerMethodField(allow_null=True, read_only=True)
    compute_time_working = serializers.SerializerMethodField(allow_null=True, read_only=True)

    class Meta:
        model = ComputeMarketplace
        fields = [
            "id",
            "name",
            "deleted_at",
            "infrastructure_id",
            "owner_id",
            "author_id",
            "catalog_id",
            "ip_address",
            "port",
            "config",
            "is_using_cpu",
            "compute_type",
            "status",
            "type",
            "file",
            "cpu_price",
            "compute_time_working",
        ]

    def get_cpu_price(self, obj):
        cpu_price_obj = ComputeGpuPrice.objects.filter(
            compute_marketplace_id=obj.id, type="cpu"
        ).first()
        if cpu_price_obj:
            return {
                "id": cpu_price_obj.id,
                "token_symbol": cpu_price_obj.token_symbol,
                "price": cpu_price_obj.price,
                "unit": cpu_price_obj.unit,
                "type": cpu_price_obj.type,
                "compute_marketplace_id": cpu_price_obj.compute_marketplace_id.id,
            }
        return None

    def get_compute_time_working(self, obj):
        compute_time_working_objs = ComputeTimeWorking.objects.filter(
            compute_id=obj.id,
            deleted_at__isnull=True,
        ).first()

        current_time = timezone.now().date()
        hours = timezone.now().time()
        if compute_time_working_objs:
            time_start = datetime.strptime(compute_time_working_objs.time_start, '%H:%M:%S').time()
            time_end = datetime.strptime(compute_time_working_objs.time_end, '%H:%M:%S').time()
            is_active_time = time_start <= hours <= time_end
            day_range = compute_time_working_objs.day_range
            is_active = False
            if day_range is not None:
                for date_range in day_range:
                    start_day = datetime.strptime(
                        date_range["start_day"], "%Y-%m-%dT%H:%M:%S.%fZ"
                    ).date()
                    end_day = datetime.strptime(
                        date_range["end_day"], "%Y-%m-%dT%H:%M:%S.%fZ"
                    ).date()
                    if start_day <= current_time <= end_day:
                        is_active= True
            # check day and time start, end
            if is_active and is_active_time:
                return {
                    "id": compute_time_working_objs.id,
                    "day_range": compute_time_working_objs.day_range,
                    "status": compute_time_working_objs.status,
                    "time_start": compute_time_working_objs.time_start,
                    "time_end": compute_time_working_objs.time_end,
                }
            return None
        return None


class ComputeMarketplaceRentV2Serializer(serializers.ModelSerializer):
    cpu_price = serializers.SerializerMethodField(allow_null=True, read_only=True)
    compute_time_working = serializers.SerializerMethodField(
        allow_null=True, read_only=True
    )

    class Meta:
        model = ComputeMarketplace
        fields = [
            "id",
            "name",
            "deleted_at",
            "infrastructure_id",
            "owner_id",
            "author_id",
            "catalog_id",
            "ip_address",
            "port",
            "config",
            "is_using_cpu",
            "compute_type",
            "status",
            "type",
            "file",
            "cpu_price",
            "compute_time_working",
        ]

    def get_cpu_price(self, obj):
        cpu_price_obj = ComputeGpuPrice.objects.filter(
            compute_marketplace_id=obj.id, type="cpu"
        ).first()
        if cpu_price_obj:
            return {
                "id": cpu_price_obj.id,
                "token_symbol": cpu_price_obj.token_symbol,
                "price": cpu_price_obj.price,
                "unit": cpu_price_obj.unit,
                "type": cpu_price_obj.type,
                "compute_marketplace_id": cpu_price_obj.compute_marketplace_id.id,
            }
        return None

    def get_compute_time_working(self, obj):
        compute_time_working_objs = ComputeTimeWorking.objects.filter(
            compute_id=obj.id,
            deleted_at__isnull=True,
        ).first()

        current_time = timezone.now().date()
        hours = timezone.now().time()
        if compute_time_working_objs:
            time_start = datetime.strptime(
                compute_time_working_objs.time_start, "%H:%M:%S"
            ).time()
            time_end = datetime.strptime(
                compute_time_working_objs.time_end, "%H:%M:%S"
            ).time()
            is_active_time = time_start <= hours <= time_end
            day_range = compute_time_working_objs.day_range
            is_active = False
            if day_range is not None:
                for date_range in day_range:
                    start_day = datetime.strptime(
                        date_range["start_day"], "%Y-%m-%dT%H:%M:%S.%fZ"
                    ).date()
                    end_day = datetime.strptime(
                        date_range["end_day"], "%Y-%m-%dT%H:%M:%S.%fZ"
                    ).date()
                    if start_day <= current_time <= end_day:
                        is_active = True
            if is_active and is_active_time:
                return {
                    "id": compute_time_working_objs.id,
                    "day_range": compute_time_working_objs.day_range,
                    "status": compute_time_working_objs.status,
                    "time_start": compute_time_working_objs.time_start,
                    "time_end": compute_time_working_objs.time_end,
                }
            return None
        return None


class ComputeRentSerializer(FlexFieldsModelSerializer):
    compute_marketplace = ComputeMarketplaceRentSerializer()
    prices = ComputeGpuPriceSerializer(many=True, read_only=True)

    class Meta:
        model = ComputeGPU
        fields = '__all__'

class TradeResourceSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Trade
        fields = [
            'token_name', 'token_symbol', 'amount', 'price',
            'type', 'resource_id', 'resource', 'resource_id'
        ]


class BulkComputeGpuSerializer(serializers.Serializer):
    compute_gpus = ComputeGpuSerializer(many=True)

    def create(self, validated_data):
        compute_gpus_data = validated_data.pop('compute_gpus')
        created_compute_gpus = []
        for compute_gpu_data in compute_gpus_data:
            created_compute_gpu = ComputeGPU.objects.create(**compute_gpu_data)
            created_compute_gpus.append(created_compute_gpu)
        return created_compute_gpus


class GpuPriceSerializer(serializers.Serializer):
    compute_gpu_id = serializers.CharField()
    token_symbol = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    compute_marketplace_id = serializers.IntegerField() 

class GpuPriceDataSerializer(serializers.Serializer):
    gpu_price = GpuPriceSerializer(many=True)
    compute_marketplace_id = serializers.IntegerField() 

class CpuPriceDataSerializer(serializers.Serializer):
    token_symbol = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    compute_marketplace_id = serializers.IntegerField() 
class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComputeGpuPrice
        fields = '__all__'

class ComputeMarketplaceDetailSerializer(ComputeMarketplaceSerializer):
    cpu_price = serializers.SerializerMethodField()
    
    def get_prices(self, instance):
        price = ComputeGpuPrice.objects.filter(
            compute_marketplace_id=instance.id,
            type='cpu'
        ).first()

        if price:
            return {
                'id': price.id,
                'token_symbol': price.token_symbol,
                'type':price.type,
                'price': price.price,
                'unit': price.unit
            }
        else:
            return None
    class Meta(ComputeMarketplaceSerializer.Meta):
        fields =('id', 'created_by', 'sortField','compute_gpus','name','created_at','updated_at','infrastructure_id','owner_id','author_id','ip_address','config','status','type','price','port','docker_port','kubernetes_port', 'compute_type', 'file', 'is_using_cpu', 'cpu_price')


class ComputeTimeWorkingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComputeTimeWorking
        fields = '__all__'

class HistoryRentComputeSerializer(serializers.ModelSerializer):
    class Meta:
        model = History_Rent_Computes
        fields = '__all__'

class ComputesPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Computes_Preference
        fields = '__all__'

class AutoMergeCardSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    # project_id = serializers.IntegerField(read_only=True)
    # token_name = serializers.CharField(read_only=True)
    # token_symbol = serializers.CharField(read_only=True)

    class Meta:
        model = Computes_Preference
        fields = '__all__'

class RecommendPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommend_Price
        fields = '__all__'
