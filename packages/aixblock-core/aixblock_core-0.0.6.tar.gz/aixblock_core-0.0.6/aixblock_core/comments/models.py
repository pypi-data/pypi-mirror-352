from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from projects.models import Project
from tasks.models import Annotation, Task


class Comment(models.Model):
    text = models.TextField(_('text'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    resolved_at = models.DateTimeField(_('updated at'), null=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        # related_name='created_projects',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('created by'),
    )

    annotation = models.ForeignKey(
        Annotation,
        # related_name='created_projects',
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_('annotation'),
        default=None,
    )

    task = models.ForeignKey(
        Task,
        # related_name='created_projects',
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_('task'),
        default=None,
    )

    project = models.ForeignKey(
        Project,
        # related_name='created_projects',
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_('project'),
        default=None,
    )

    is_resolved = models.BooleanField(_('is resolved'), default=False)

    def __init__(self, *args, **kwargs):
        super(Comment, self).__init__(*args, **kwargs)

    def has_permission(self, user):
        return not self.project or self.project.has_permission(user)
