from rest_framework import serializers
from .models import Order
from compute_marketplace.models import ComputeGPU, ComputeMarketplace, Trade, History_Rent_Computes
from compute_marketplace.serializers import HistoryRentComputeSerializer
import django_filters
from django.db.models import Q

class ComputeMarketplaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComputeMarketplace
        fields = '__all__'

class ComputeGPUSerializer(serializers.ModelSerializer):
    compute_marketplace = ComputeMarketplaceSerializer()
    history_order = serializers.SerializerMethodField()

    def get_history_order(self, obj):
        history_instance = History_Rent_Computes.objects.filter(compute_gpu_id = obj.id).first()
        if history_instance:
            return HistoryRentComputeSerializer(history_instance).data
        else:
            return None

    class Meta:
        model = ComputeGPU
        fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):
    compute_gpus = serializers.SerializerMethodField()

    def get_compute_gpus(self, obj):
        compute_gpus = obj.compute_gpus.all()
        return ComputeGPUSerializer(compute_gpus, many=True).data

    class Meta:
        model = Order
        fields = "__all__"

class OrderFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    status = django_filters.CharFilter(lookup_expr="icontains")
    catalog_id = django_filters.NumberFilter()
    all = django_filters.CharFilter(method="filter_all")

    class Meta:
        model = Order
        fields = ["total_amount", "status", "unit", "all"]

    def filter_all(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(name__icontains=value) | Q(status__icontains=value)
            )
        return queryset


class TradePaymentSerializer(serializers.Serializer):
    class Meta:
        model = Trade
        fields = "__all__"
