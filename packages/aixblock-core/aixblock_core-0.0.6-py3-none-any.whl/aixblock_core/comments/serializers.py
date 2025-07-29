from comments.models import Comment
from rest_flex_fields import FlexFieldsModelSerializer
from users.models import User
from users.serializers import BaseUserSerializer


class CommentCreatedBySerializer(BaseUserSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'avatar')


class CommentSerializer(FlexFieldsModelSerializer):
    created_by = CommentCreatedBySerializer(default=None, help_text='Comment creator')

    class Meta:
        model = Comment
        fields = '__all__'
