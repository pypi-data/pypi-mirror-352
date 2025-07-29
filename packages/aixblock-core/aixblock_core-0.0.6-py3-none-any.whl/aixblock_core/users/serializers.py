"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
from rest_framework import serializers
from rest_flex_fields import FlexFieldsModelSerializer
from django.conf import settings

from .models import User, Notification, Rank_Point, Transaction
from reward_point.models import User_Point
from core.utils.common import load_func
from compute_marketplace.models import Portfolio

class BaseUserSerializer(FlexFieldsModelSerializer):
    # short form for user presentation
    initials = serializers.SerializerMethodField(default='?', read_only=True)
    avatar = serializers.SerializerMethodField(read_only=True)
    rank_point_name = serializers.SerializerMethodField()
    point = serializers.SerializerMethodField()
    centrifuge_token = serializers.SerializerMethodField()

    def get_centrifuge_token(self, obj):
        return getattr(obj, 'centrifuge_token', None)
    def get_avatar(self, user):
        return user.avatar_url

    def get_initials(self, user):
        return user.get_initials()

    def get_rank_point_name(self, user):
        rank_point = user.rank_point
        if rank_point:
            return rank_point.name
        return None

    def get_point(self, user):
        user_point = User_Point.objects.filter(user=user).first()
        if user_point:
            return user_point.point
        return None

    def to_representation(self, instance):
        """ Returns user with cache, this helps to avoid multiple s3/gcs links resolving for avatars """

        uid = instance.id
        key = 'user_cache'

        if key not in self.context:
            self.context[key] = {}
        if uid not in self.context[key]:
            self.context[key][uid] = super().to_representation(instance)

        return self.context[key][uid]

    class Meta:
        model = User
        fields = (
            'id',
            'uuid',
            'first_name',
            'last_name',
            'username',
            'email',
            'last_activity',
            'avatar',
            'initials',
            'phone',
            'active_organization',
            'is_organization_admin',
            'is_freelancer',
            'allow_newsletters',
            'is_active',
            'is_superuser',
            'is_qa',
            'is_qc',
            'is_model_seller',
            'is_compute_supplier',
            'is_labeler',
            'date_joined',
            'rank_point_name',
            'point',
            'is_verified',
            'centrifuge_token'
        )


class UserSimpleSerializer(BaseUserSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'avatar') #,'username'

class UserSuperSimpleSerializer(BaseUserSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name') #,'username'


class UserCompactSerializer(BaseUserSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'avatar', 'username')


class AdminUserListSerializer(BaseUserSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'username',
            'email',
            'password',
            'last_activity',
            'avatar',
            'initials',
            'phone',
            'active_organization',
            'is_organization_admin',
            'is_freelancer',
            'allow_newsletters',
            'is_active',
            'is_superuser',
            'is_qa',
            'is_qc',
            'is_model_seller',
            'is_compute_supplier',
            'is_labeler',
            'date_joined',
            'rank_point',
            'is_verified',
        )


UserSerializer = load_func(settings.USER_SERIALIZER)


class NotificationSerializer(FlexFieldsModelSerializer):
    time = serializers.DateTimeField()

    class Meta:
        model = Notification
        fields = ('id', 'content', 'link', 'is_read', 'time')

class DetailNotificationSerializer(FlexFieldsModelSerializer):
    time = serializers.DateTimeField()

    class Meta:
        model = Notification
        fields = ('id', 'content', 'link', 'is_read', 'time', 'detail', 'deleted_at', 'type', 'status', 'history_id')

class UserAdminViewSerializer(BaseUserSerializer, serializers.ModelSerializer):
    active_organization = serializers.SlugRelatedField(read_only=True,slug_field='title')
    class Meta:
        model = User
        fields = (
            'id', 'username', 'active_organization', 'is_organization_admin', 'email', 'date_joined',
            'is_active', 'is_superuser', 'is_qa', 'is_qc', 'is_staff', 'rank_point', 'is_verified'
        )

class UserRegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=50)
    password = serializers.CharField(min_length=6, max_length=30)
    role = serializers.IntegerField()
    class Meta:
        model = User
        fields = ('first_name', 'email', 'password', 'role')

class RankPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rank_Point
        fields = ['name', 'minimum_points']


class ChangePasswordSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    class Meta:
        model = User
        fields = ['email', 'password']

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    class Meta:
        model = User
        fields = ['email']

class PasswordResetConfirmView(serializers.Serializer):
    password = serializers.CharField(required=True)
    class Meta:
        model = User
        fields = ['password']


class PortfolioSerializer(FlexFieldsModelSerializer):

    class Meta:
        model = Portfolio
        fields = "__all__"


class ValidateEmailSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['email']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
