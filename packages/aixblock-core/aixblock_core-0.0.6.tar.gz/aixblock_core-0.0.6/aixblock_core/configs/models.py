from django.db import models
from django.utils.translation import gettext_lazy as _


class InstallationService(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    version = models.TextField(null=True, max_length=10)
    image = models.TextField(null=True)
    registry = models.TextField(null=True)
    class Environment(models.TextChoices):
        PRODUCTION = (
            "prod",
            _("Production"),
        )
        DEVELOPMENT = "dev", _("Development")
        STAGING = "stg", _("Staging")

    environment = models.CharField(
        _("environment"),
        max_length=64,
        choices=Environment.choices,
        default=Environment.DEVELOPMENT,
        null=True,
    )

    class Status(models.TextChoices):
        ACTIVE = "active", _("active"),
        INACTIVE = "inactive", _("inactive")
        ERROR = "error", _("error")

    status = models.CharField(
        _("status"),
        max_length=64,
        choices=Status.choices,
        default=Status.ACTIVE,
        null=True,
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True, null=True)
    deleted_at = models.DateTimeField(_("deleted at"), null=True)
    def __init__(self, *args, **kwargs):
        super(InstallationService, self).__init__(*args, **kwargs)

    def has_permission(self, user):
        return self
