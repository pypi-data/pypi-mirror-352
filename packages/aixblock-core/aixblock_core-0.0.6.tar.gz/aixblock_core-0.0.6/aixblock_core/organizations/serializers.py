"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import ujson as json

from rest_framework import serializers
from drf_dynamic_fields import DynamicFieldsMixin

from organizations.models import Organization, OrganizationMember
from users.serializers import UserSerializer
from collections import OrderedDict
from users.models import User

class OrganizationIdSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'title', 'status']


class OrganizationSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    class Meta:
        model = Organization
        fields = '__all__'

class OrganizationModelSerializer(serializers.ModelSerializer):
    # created_by = serializers.SlugRelatedField(read_only=True,slug_field='email')
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    class Meta:
        model = Organization
        fields = '__all__'

class OrganizationMemberSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = OrganizationMember
        fields = ['id', 'organization', 'user', 'is_admin']


class UserSerializerWithProjects(UserSerializer):
    created_projects = serializers.SerializerMethodField(read_only=True)
    contributed_to_projects = serializers.SerializerMethodField(read_only=True)

    def get_created_projects(self, user):
        if not self.context.get('contributed_to_projects', False):
            return None

        current_user = self.context['request'].user
        return user.created_projects.filter(organization=current_user.active_organization).values('id', 'title')

    def get_contributed_to_projects(self, user):
        if not self.context.get('contributed_to_projects', False):
            return None

        current_user = self.context['request'].user
        projects = user.annotations\
            .filter(task__project__organization=current_user.active_organization)\
            .values('task__project__id', 'task__project__title')
        contributed_to = [(json.dumps({'id': p['task__project__id'], 'title': p['task__project__title']}), 0)
                          for p in projects]
        contributed_to = OrderedDict(contributed_to)  # remove duplicates without ordering losing
        return [json.loads(key) for key in contributed_to]

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('created_projects', 'contributed_to_projects')


class OrganizationMemberUserSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    """Adds all user properties"""
    user = UserSerializerWithProjects()

    class Meta:
        model = OrganizationMember
        fields = ['id', 'organization', 'user', 'is_admin']


class OrganizationInviteSerializer(serializers.Serializer):
    token = serializers.CharField(required=False)
    invite_url = serializers.CharField(required=False)


class OrganizationsParamsSerializer(serializers.Serializer):
    active = serializers.BooleanField(required=False, default=False)
    contributed_to_projects = serializers.BooleanField(required=False, default=False)
class OrganizationReporRequest(serializers.Serializer):
    project_id = serializers.IntegerField(
        help_text='ID of project',
        required=True,
    )
    roles = serializers.CharField(
        help_text='role name: is_annotator,is_qa,is_qc',
        required=True
    )
    