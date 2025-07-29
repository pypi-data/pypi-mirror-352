"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import logging

from django.db import models, transaction
from django.conf import settings
from django.db.models import Q, Count
from django.utils.translation import gettext_lazy as _
import users.models as users_models
from core.utils.common import create_hash, get_object_with_check_and_log, get_organization_from_request, load_func

logger = logging.getLogger(__name__)


class OrganizationMember(models.Model):
    """
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='om_through',
        help_text='User ID'
    )
    organization = models.ForeignKey(
        'organizations.Organization', on_delete=models.CASCADE,
        help_text='Organization ID'
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    is_admin = models.BooleanField(_('is_admin'), default=False,
                                     help_text='is admin of Organization', blank=True)

    level_org = models.BooleanField(_('level_org'), default=True,
                                     help_text='level of org', blank=True)
    @classmethod
    def find_by_user(cls, user_or_user_pk, organization_pk):
        from users.models import User

        user_pk = user_or_user_pk.pk if isinstance(user_or_user_pk, User) else user_or_user_pk
        return OrganizationMember.objects.get(user=user_pk, organization=organization_pk)

    @property
    def is_owner(self):
        return self.user.id == self.organization.created_by.id

    class Meta:
        ordering = ['pk']

    def has_permission(self, user):
        return (OrganizationMember.objects
                .filter(user=user)
                .filter(organization=self.organization)
                .filter(is_admin=True)
                .exists()
                )


OrganizationMixin = load_func(settings.ORGANIZATION_MIXIN)


class Organization(OrganizationMixin, models.Model):
    title = models.CharField(_('organization title'), max_length=1000, null=False)

    token = models.CharField(_('token'), max_length=256, default=create_hash, unique=True, null=True, blank=True)
    team_id = models.CharField(_('team_id'), max_length=256, default=create_hash, unique=True, null=True)

    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="organizations", through=OrganizationMember)

    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, related_name="organization",
                                   null=True, verbose_name=_('created_by'))

    # created_by = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
    #                                   null=True, related_name="organization", verbose_name=_('created_by'))

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    class Status(models.TextChoices):
        ACTIVED = 'actived', _('Actived')
        PENDING = 'pending', _('Pending')
        SUPPEND = 'suppend', _('Suppend')
    status = models.CharField(
        _('status'),
        max_length=64,
        choices=Status.choices,
        default=Status.PENDING,
    )
    def __str__(self):
        return self.title + ', id=' + str(self.pk)

    @classmethod
    def from_request(cls, request):
        if 'organization_pk' not in request.session:
            logger.debug('"organization_pk" is missed in request.session: can\'t get Organization')
            return
        pk = get_organization_from_request(request)
        return get_object_with_check_and_log(request, Organization, pk=pk)

    @classmethod
    def create_organization(cls, created_by=None, title='Your Organization'):
        _create_organization = load_func(settings.CREATE_ORGANIZATION)
        return _create_organization(title=title, created_by=created_by)

    @classmethod
    def create_team_organization(cls, team_id, created_by=None):
        org = Organization.objects.create(title='Team #' + team_id, team_id=team_id, created_by=created_by)
        return OrganizationMember.objects.create(user=created_by, organization=org)
        # return organizations.functions.create_team_organization(team_id=team_id, created_by=created_by)

    @classmethod
    def find_by_user(cls, user):
        memberships = OrganizationMember.objects.filter(user=user).prefetch_related('organization')
        if not memberships.exists():
            raise ValueError(f'No memberships found for user {user}')
        return memberships.first().organization

    @classmethod
    def find_by_team_id(cls, team_id):
        return Organization.objects.filter(team_id=team_id).first()

    @classmethod
    def find_by_invite_url(cls, url):
        token = url.strip('/').split('/')[-1]
        if len(token):
            return Organization.objects.get(token=token)
        else:
            raise KeyError(f'Can\'t find Organization by welcome URL: {url}')

    def has_user(self, user):
        return self.users.filter(pk=user.pk).exists()

    def has_project_member(self, user):
        return self.projects.filter(members__user=user).exists()

    def has_permission(self, user):
        if self in user.organizations.all():
            return True
        return False

    def add_user(self, user):
        if self.users.filter(pk=user.pk).exists():
            logger.debug('User already exists in organization.')
            return

        with transaction.atomic():
            om = OrganizationMember(user=user, organization=self)
            om.save()

            return om    
    
    def reset_token(self):
        self.token = create_hash()
        self.save()

    def check_max_projects(self):
        """This check raise an exception if the projects limit is hit
        """
        pass

    def projects_sorted_by_created_at(self):
        return self.projects.all().order_by('-created_at').annotate(
            tasks_count=Count('tasks'),
            labeled_tasks_count=Count('tasks', filter=Q(tasks__is_labeled=True))
        ).prefetch_related('created_by')

    def created_at_prettify(self):
        return self.created_at.strftime("%d %b %Y %H:%M:%S")

    def per_project_invited_users(self):
        from users.models import User

        invited_ids = self.projects.values_list('members__user__pk', flat=True).distinct()
        per_project_invited_users = User.objects.filter(pk__in=invited_ids)
        return per_project_invited_users

    @property
    def secure_mode(self):
        return False

    @property
    def members(self):
        return OrganizationMember.objects.filter(organization=self)

    class Meta:
        db_table = 'organization'


class Organization_Project_Permission(models.Model):
    organization = models.ForeignKey(
        'organizations.Organization', on_delete=models.CASCADE,
        help_text='Organization ID'
    )

    project_id = models.ForeignKey(
        'projects.Project', on_delete=models.CASCADE,
        help_text='Project ID'
    )

    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, related_name="organization_project",
                            null=True, verbose_name=_('created_by'))
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    deleted_at = models.DateTimeField(_('deleted at'), null=True)

    is_labeler = models.BooleanField(_('is labeler'), default=False, null=True)
    is_qa = models.BooleanField(_('is QA'), default=False, null=True)
    is_qc = models.BooleanField(_('is QC'), default=False, null=True)
