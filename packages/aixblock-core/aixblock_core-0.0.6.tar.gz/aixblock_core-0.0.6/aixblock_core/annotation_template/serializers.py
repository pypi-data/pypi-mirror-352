from .models import AnnotationTemplate
from rest_flex_fields import FlexFieldsModelSerializer
from model_marketplace.models import CatalogModelMarketplace
from rest_framework import serializers
class CatalogModelMarketplaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogModelMarketplace
        fields = ("id", "key", "name", "status")


class AnnotationTemplateserializer(FlexFieldsModelSerializer):
    class Meta:
        model = AnnotationTemplate
        fields = '__all__'


class AnnotationDetailTemplateserializer(serializers.ModelSerializer):
    catalog_model = serializers.SerializerMethodField()

    class Meta:
        model = AnnotationTemplate
        fields = "__all__"
        ref_name = "AnnotationTemplateDetail"

    def get_catalog_model(self, obj):
        catalog_model_id = obj.catalog_model_id
        if catalog_model_id:
            catalog_model = CatalogModelMarketplace.objects.get(pk=catalog_model_id)
            serializer = CatalogModelMarketplaceSerializer(catalog_model)
            return serializer.data
        return None
