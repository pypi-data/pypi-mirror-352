"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import logging
import rules

from pydantic import BaseModel
from typing import Optional

from rest_framework.permissions import BasePermission

logger = logging.getLogger(__name__)


class AllPermissions(BaseModel):
    organizations_create = 'organizations.create'
    organizations_view = 'organizations.view'
    organizations_change = 'organizations.change'
    organizations_delete = 'organizations.delete'
    organizations_invite = 'organizations.invite'
    projects_create = 'projects.create'
    projects_view = 'projects.view'
    projects_change = 'projects.change'
    projects_delete = 'projects.delete'
    tasks_create = 'tasks.create'
    tasks_view = 'tasks.view'
    tasks_change = 'tasks.change'
    tasks_delete = 'tasks.delete'
    annotations_create = 'annotations.create'
    annotations_view = 'annotations.view'
    annotations_change = 'annotations.change'
    annotations_delete = 'annotations.delete'
    actions_perform = 'actions.perform'
    predictions_any = 'predictions.any'
    avatar_any = 'avatar.any'
    labels_create = 'labels.create'
    labels_view = 'labels.view'
    labels_change = 'labels.change'
    labels_delete = 'labels.delete'
    model_marketplace_create = 'model_marketplace.create'
    model_marketplace_view = 'model_marketplace.view'
    model_marketplace_change = 'model_marketplace.change'
    model_marketplace_delete = 'model_marketplace.delete'
    orders_delete = 'orders.delete'
    orders_view = 'orders.view'
    orders_change = 'orders.change'
    orders_create = 'orders.create'
    reward_point_view = "reward_point.view"
    reward_point_change = "reward_point.change"
    reward_point_delete = "reward_point.delete"
    reward_point_create = "reward_point.create"
    installation_service_view = "installation_service.view"
    installation_service_change = "installation_service.change"
    installation_service_delete = "installation_service.delete"
    installation_service_create = "installation_service.create"


all_permissions = AllPermissions()


class ViewClassPermission(BaseModel):
    GET: Optional[str] = None
    PATCH: Optional[str] = None
    PUT: Optional[str] = None
    DELETE: Optional[str] = None
    POST: Optional[str] = None


def make_perm(name, pred, overwrite=False):
    if rules.perm_exists(name):
        if overwrite:
            rules.remove_perm(name)
        else:
            return
    rules.add_perm(name, pred)


for _, permission_name in all_permissions:
    make_perm(permission_name, rules.is_authenticated)


class IsSuperAdmin(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)
    
class IsSuperAdminOrg(BasePermission):
    """
    Allows access only to admin org users.
    """

    def has_permission(self, request, view):
        try:
            from organizations.models import OrganizationMember
            from projects.models import Project

            if 'project_id' in request.data:
                project = Project.objects.get(id=request.data.get('project_id'))
            else:
                project = Project.objects.get(id=request.data.get('project'))
            check_org_admin = OrganizationMember.objects.filter(organization_id = project.organization_id, user_id=request.user.id, is_admin=True).exists()
            if not check_org_admin:
                if not project.organization.created_by_id == request.user.id and not request.user.is_superuser:
                    return False
            return True
        except:
            return True

def permission_org(user, project):
    try:
        from organizations.models import OrganizationMember

        check_org_admin = OrganizationMember.objects.filter(organization_id = project.organization_id, user_id=user.id, is_admin=True).exists()
        if not check_org_admin:
            if not project.organization.created_by_id == user.id and not user.is_superuser:
                return False
        return True
    except:
        return True