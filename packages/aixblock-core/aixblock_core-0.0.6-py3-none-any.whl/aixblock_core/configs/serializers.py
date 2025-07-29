from rest_framework import serializers
from .models import InstallationService


class InstallationServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallationService
        fields = "__all__"


class InstallationServiceAfterDeploySerializer(serializers.ModelSerializer):
    key = serializers.CharField(required=True)
    class Meta:
        model = InstallationService
        fields = "__all__"
