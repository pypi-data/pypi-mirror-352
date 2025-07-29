from django.db import transaction

from core.utils.common import temporary_disconnect_all_signals
from organizations.models import Organization, OrganizationMember
from projects.models import Project


def create_organization(title, created_by):
    with transaction.atomic():
        org = Organization.objects.create(title=title, created_by=created_by)
        OrganizationMember.objects.create(user=created_by, organization=org)
        return org


def create_team_organization(team_id, created_by):
    with transaction.atomic():
        org = Organization.objects.create(title='Team #' + team_id, team_id=team_id, created_by=created_by)
        OrganizationMember.objects.create(user=created_by, organization=org)
        return org


def destroy_organization(org):
    with temporary_disconnect_all_signals():
        Project.objects.filter(organization=org).delete()
        if hasattr(org, 'saml'):
            org.saml.delete()
        org.delete()

def has_admin_permission_org(user_id, org_id):
    """
    Check if the user has admin permission in the organization.
    """
    current_organization_user = OrganizationMember.objects.filter(
        organization=org_id, user_id=user_id
    ).first()
    if not current_organization_user:
        return False
    return current_organization_user.is_admin or current_organization_user.is_owner