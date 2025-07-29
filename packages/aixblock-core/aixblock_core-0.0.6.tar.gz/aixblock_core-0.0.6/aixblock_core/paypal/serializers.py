from rest_framework import serializers


class CreateOrderSerializer(serializers.Serializer):
    amount = serializers.FloatField(required=True)


class CaptureOrderSerializer(serializers.Serializer):
    order_id = serializers.CharField(required=True)