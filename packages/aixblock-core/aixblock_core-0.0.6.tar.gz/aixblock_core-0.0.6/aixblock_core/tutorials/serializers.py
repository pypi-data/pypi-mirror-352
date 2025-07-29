from rest_framework import serializers
from .models import TutorialGroup, TutorialSubGroup, TutorialSectionContent, TutorialContent

class TutorialContentSerializer(serializers.ModelSerializer):

    class Meta:
        model = TutorialContent
        fields = '__all__'

class TutorialSectionContentSerializer(serializers.ModelSerializer):
    tutorial_content = TutorialContentSerializer(many=False, read_only=True)

    class Meta:
        model = TutorialSectionContent
        fields = '__all__'

class TutorialSubGroupSerializer(serializers.ModelSerializer):
    section_contents = TutorialSectionContentSerializer(many=True, read_only=True)
    class Meta:
        model = TutorialSubGroup
        fields = '__all__'

class TutorialGroupSerializer(serializers.ModelSerializer):
    sub_groups = TutorialSubGroupSerializer(many=True, read_only=True)
    keyword = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = TutorialGroup
        fields = '__all__'

class DocumentBlockSerializer(serializers.Serializer):
    block_id = serializers.CharField()
    block_title = serializers.CharField()

class DocumentSubPageSerializer(serializers.Serializer):
    page_id = serializers.CharField()
    page_title = serializers.CharField()

class DocumentPageSerializer(serializers.Serializer):
    page_id = serializers.CharField()
    page_title = serializers.CharField()
    sub_pages = DocumentSubPageSerializer(many=True)

class DocumentPageListSerializer(serializers.Serializer):
    pages = DocumentPageSerializer(many=True)
