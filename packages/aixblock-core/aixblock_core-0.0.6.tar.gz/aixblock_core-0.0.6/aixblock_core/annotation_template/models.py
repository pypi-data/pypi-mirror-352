from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_marketplace.models import CatalogModelMarketplace

class AnnotationTemplate(models.Model):
    name = models.TextField(_('name'))
    group = models.TextField(_('group'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), null=True, auto_now_add=True)
    author_id = models.IntegerField(_('author id'))
    order = models.IntegerField(_('order'))
    image = models.TextField(_('image'), default='')
    details = models.TextField(_('ml details'), default='')
    ml_image = models.TextField(_('ml_image'))
    ml_ip = models.TextField(_('ml_ip'))
    ml_port = models.TextField(_('ml_port'))
    config = models.TextField(_('config'))
    status = models.BooleanField(_('status'), default=False)
    infrastructure_id = models.TextField(_('infrastructure id'), default='', null=True, blank=True)
    data_type = models.TextField(_('data_type'), default='', null=True, blank=True)
    extensions = models.TextField(_('extensions'), default='', null=True, blank=True)
    catalog_model_id = models.IntegerField(_("catalog model id"), null=True)
    catalog_key = models.TextField(_("catalog_key"), null=True)
    is_deleted = models.BooleanField(_('is_deleted'), default=False, null=True)

    def __init__(self, *args, **kwargs):
        super(AnnotationTemplate, self).__init__(*args, **kwargs)

    def has_permission(self, user):
        return self
    class Meta:
        db_table = 'annotation_template_annotation_template'
