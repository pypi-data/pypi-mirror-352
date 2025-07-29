"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import datetime
import uuid
from enum import Enum

from django.utils import timezone
from django.conf import settings
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token

from organizations.models import OrganizationMember, Organization
from users.functions import hash_upload
from core.utils.common import load_func
# from projects.models import Project

YEAR_START = 1980
YEAR_CHOICES = []
for r in range(YEAR_START, (datetime.datetime.now().year+1)):
    YEAR_CHOICES.append((r, r))

year = models.IntegerField(_('year'), choices=YEAR_CHOICES, default=datetime.datetime.now().year)


class UserRole(int, Enum):
    compute_supplier = 1
    model_developer = 2
    model_seller = 3
    labeler = 4


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        try:
            if not email:
                raise ValueError('Must specify an email address')

            email = self.normalize_email(email)
            user = self.model(email=email, **extra_fields)

            user.set_password(password)
            user.save(using=self._db)

            return user
        except Exception as e:
            print(e)

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class UserLastActivityMixin(models.Model):
    last_activity = models.DateTimeField(
        _('last activity'), default=timezone.now, editable=False)

    def update_last_activity(self):
        self.last_activity = timezone.now()
        self.save(update_fields=["last_activity"])

    class Meta:
        abstract = True


UserMixin = load_func(settings.USER_MIXIN)


class User(UserMixin, AbstractBaseUser, PermissionsMixin, UserLastActivityMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username and password are required. Other fields are optional.
    """
    username = models.CharField(_('username'), max_length=256)
    email = models.EmailField(_('email address'), unique=True, blank=True)

    first_name = models.CharField(_('first name'), max_length=256, blank=True)
    last_name = models.CharField(_('last name'), max_length=256, blank=True)
    phone = models.CharField(_('phone'), max_length=256, blank=True)
    avatar = models.ImageField(upload_to=hash_upload, blank=True)

    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin site.'))

    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether to treat this user as active. '
                                                'Unselect this instead of deleting accounts.'))
    is_compute_supplier = models.BooleanField(_('is compute supplier'), default=False,
                                   help_text=_('Designates whether the user can log into this admin site.'))
    is_model_seller = models.BooleanField(_('is model seller'), default=False,
                                   help_text=_('Designates whether the user can log into this admin site.'))
    is_labeler = models.BooleanField(_('is labeler'), default=False, null=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    activity_at = models.DateTimeField(_('last annotation activity'), auto_now=True)

    active_organization = models.ForeignKey(
        'organizations.Organization',
        null=True,
        on_delete=models.SET_NULL,
        related_name='active_users'
    )

    allow_newsletters = models.BooleanField(
        _('allow newsletters'),
        null=True,
        default=None,
        help_text=_('Allow sending newsletters to user')
    )

    is_qa = models.BooleanField(_('is QA'), default=False,
                                    help_text=_('Designates whether the user can review tasks.'))

    is_qc = models.BooleanField(_('is QC'), default=False,
                                    help_text=_('Designates whether the user can qualify tasks.'))

    rank_point = models.ForeignKey('Rank_Point', on_delete=models.SET_NULL, null=True)

    is_verified = models.BooleanField(_('verified'), default=True,
                                    help_text=_('Designates whether to treat this user as a verified.'))
    
    uuid = models.TextField(default=uuid.uuid4, unique=True, verbose_name='UUID', null=True, editable=False)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ()

    class Meta:
        db_table = 'htx_user'
        verbose_name = _('user')
        verbose_name_plural = _('users')
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['first_name']),
            models.Index(fields=['last_name']),
            models.Index(fields=['date_joined']),
        ]

    @property
    def avatar_url(self):
        if self.avatar:
            if settings.CLOUD_FILE_STORAGE_ENABLED:
                return self.avatar.url
            else:
                return settings.HOSTNAME + self.avatar.url

    def active_organization_annotations(self):
        return self.annotations.filter(task__project__organization=self.active_organization)

    def active_organization_contributed_project_number(self):
        annotations = self.active_organization_annotations()
        return annotations.values_list('task__project').distinct().count()

    @property
    def own_organization(self):
        return Organization.objects.get(created_by=self)

    @property
    def has_organization(self):
        return Organization.objects.filter(created_by=self).exists()

    @property
    def is_organization_admin(self):
        """
        Returns True if this user is the admin of current active_organization
        """
        return (OrganizationMember.objects
                .filter(organization=self.active_organization)
                .filter(user=self)
                .filter(is_admin=True)
                .exists()
                )

    @property
    def is_freelancer(self):
        """
        Returns True if this user is the admin of current active_organization
        """
        if self.is_superuser or self.is_organization_admin or self.is_compute_supplier or self.is_model_seller or self.is_labeler:
            return False

        return (OrganizationMember.objects
                .filter(organization=self.active_organization)
                .filter(user=self)
                .filter(level_org=False)
                .exists()
                )

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def name_or_email(self):
        name = self.get_full_name()
        if len(name) == 0:
            name = self.email

        return name
        
    def get_full_name(self):
        """
        Return the first_name and the last_name for a given user with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def reset_token(self):
        token = Token.objects.filter(user=self)
        if token.exists():
            token.delete()
        return Token.objects.create(user=self)
    
    def get_initials(self):
        initials = '?'
        if not self.first_name and not self.last_name:
            initials = self.email[0:2]
        elif self.first_name and not self.last_name:
            initials = self.first_name[0:1]
        elif self.last_name and not self.first_name:
            initials = self.last_name[0:1]
        elif self.first_name and self.last_name:
            initials = self.first_name[0:1] + self.last_name[0:1]
        return initials


@receiver(post_save, sender=User)
def init_user(sender, instance=None, created=False, **kwargs):
    if created:
        # create token for user
        Token.objects.create(user=instance)


class Notification(models.Model):
    content = models.CharField(_('content'), max_length=256)
    link = models.CharField(_('link'), max_length=256, null=True)
    is_read = models.BooleanField(_('is read'), default=False)
    time = models.DateTimeField(_('time'), auto_now=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name="notification",
                                   null=True, verbose_name=_('user'))
    
    detail = models.TextField(_('detail'), null=True)
    deleted_at = models.DateTimeField(_('deleted_at'), null=True)
    type = models.TextField(_('type'), null=True)
    history_id = models.IntegerField(_('history_id'), null=True)

    class Meta:
        ordering = ["-time"]

    class Status(models.TextChoices):
        Info = 'info', _('Info')
        Sucessful = 'success', _('Success')
        Danger = 'danger', _('Danger')
        Warning = 'warning', _('Warning')
        Default = 'default', _('Default')
    
    status = models.CharField(
        _('status'),
        max_length=64,
        choices=Status.choices,
        default=Status.Info,
        null=True
    )

class Rank_Point(models.Model):
    name = models.CharField(max_length=255,null=False)
    minimum_points = models.IntegerField(default = 0)

class Transaction(models.Model):
    user_id = models.IntegerField(_('user id'), null=False)
    order_id = models.IntegerField(_('order id'), null=True)
    amount = models.FloatField(_('amount'), null=True)
    description = models.CharField(max_length=255,null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), null=True, auto_now_add=True)
    deleted_at = models.DateTimeField(_("deleted at"), null=True)
    wallet_address = models.CharField(max_length=255, null=True)
    
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        SUCCESS = 'success', _('Success')
        FAILED = 'failed', _('Failed')

    status = models.CharField(
        _('status'),
        max_length=64,
        choices=Status.choices,
        default=Status.SUCCESS,
        null=True
    )
    class Unit(models.TextChoices):
        USDC = "usdc", _("Usdc")
        USD = "usd", _("Usd")
        SOL = "sol", _("Sol")

    unit = models.CharField(
        _("unit"),
        max_length=50,
        choices=Unit.choices,
        null=True,
    )

    class Network(models.TextChoices):
        FIAT = "fiat", _("Fiat")
        PAYPAL = "paypal", _("PayPal")
        STRIPE = "stripe", _("Stripe")
        SOLANA = "solana", _("Solana")
    
    network = models.CharField(
        _("network"),
        max_length=50,
        choices=Network.choices,
        null=True,
    )
        
    class Type(models.TextChoices):
        RENT_COMPUTE = "rent_compute", _("Rent compute")
        REFUND_COMPUTE = "refund_compute", _("Refund compute") # self host
        RENT_MODEL = "rent_model", _("Rent model")
        REFUND_MODEL = "refund_model", _("Refund model") # self host
        WITHDRAW = "withdraw", _("Withdraw")
        TOPUP = "topup", _("Topup")

    type = models.CharField(
        _("type"),
        max_length=50,
        choices=Type.choices,
        null=True,
    )